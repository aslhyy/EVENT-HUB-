"""
Views para asistentes.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import csv
from django.http import HttpResponse
from django.db import models
from core.emails import EmailService

import logging
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status

from .models import Attendee, CheckInLog, Survey, SurveyQuestion, SurveyResponse
from .serializers import (
    AttendeeSerializer, AttendeeDetailSerializer, CheckInSerializer,
    CheckInLogSerializer, SurveySerializer, SurveyDetailSerializer,
    SurveyQuestionSerializer, SurveyResponseSerializer,
    SubmitSurveySerializer, AttendeeExportSerializer
)
from .filters import AttendeeFilter
from apps.tickets.models import Ticket
from core.permissions import IsEventOrganizer

logger = logging.getLogger(__name__)

class AttendeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de asistentes.
    
    list: Listar asistentes
    retrieve: Obtener detalle de asistente
    create: Crear asistente
    update: Actualizar asistente
    check_in: Realizar check-in
    my_attendances: Obtener asistencias del usuario
    export: Exportar asistentes a CSV
    """
    queryset = Attendee.objects.select_related(
        'user', 'ticket', 'event', 'checked_in_by'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AttendeeFilter
    search_fields = ['full_name', 'email', 'document_number']
    ordering_fields = ['created_at', 'checked_in_at', 'status']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AttendeeDetailSerializer
        elif self.action == 'check_in':
            return CheckInSerializer
        elif self.action == 'export':
            return AttendeeExportSerializer
        return AttendeeSerializer

    def get_queryset(self):
        """Filtrar asistencias del usuario o eventos organizados."""
        user = self.request.user
        if user.is_staff:
            return self.queryset
        
        # Ver sus propias asistencias o eventos que organiza
        return self.queryset.filter(
            models.Q(user=user) | models.Q(event__organizer=user)
        )

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def check_in(self, request):
        """
        Realizar check-in de un asistente.
        """
        serializer = CheckInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        ticket_code = serializer.validated_data.get('ticket_code')
        ticket_uuid = serializer.validated_data.get('ticket_uuid')
        location = serializer.validated_data.get('location', '')
        notes = serializer.validated_data.get('notes', '')
        
        try:
            # Buscar ticket
            if ticket_code:
                ticket = Ticket.objects.get(code=ticket_code)
            else:
                ticket = Ticket.objects.get(uuid=ticket_uuid)
            
            # Buscar o crear asistente
            attendee, created = Attendee.objects.get_or_create(
                ticket=ticket,
                event=ticket.ticket_type.event,
                defaults={
                    'user': ticket.buyer,
                    'full_name': ticket.attendee_name,
                    'email': ticket.attendee_email,
                    'phone': ticket.attendee_phone,
                }
            )
            
            # Verificar si puede hacer check-in
            if not attendee.can_check_in:
                return Response(
                    {'error': 'No se puede realizar check-in en este momento'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Registrar check-in
            check_in_log = CheckInLog.objects.create(
                attendee=attendee,
                checked_in_by=request.user,
                location=location,
                notes=notes,
                ip_address=self.get_client_ip(request)
            )

            # Enviar confirmación de check-in
            try:
                EmailService.send_check_in_confirmation(attendee)
            except Exception as e:
                logger.error(f"Error enviando email de check-in: {e}")
            
            # Actualizar estado del asistente
            if attendee.status == 'registered':
                attendee.status = 'checked_in'
                attendee.checked_in_at = timezone.now()
                attendee.checked_in_by = request.user
                attendee.save()

            # Enviar confirmación de check-in
            from core.emails import EmailService
            import logging
            logger = logging.getLogger(__name__)

            try:
                EmailService.send_check_in_confirmation(attendee)
                logger.info(f"Email de check-in enviado para {attendee.email}")
            except Exception as e:
                logger.error(f"Error enviando email de check-in: {e}")
            
            # Marcar ticket como usado si es el primer check-in
            if ticket.status == 'active' and attendee.total_check_ins == 1:
                ticket.status = 'used'
                ticket.used_at = timezone.now()
                ticket.save()
            
            return Response({
                'message': 'Check-in realizado exitosamente',
                'attendee': AttendeeDetailSerializer(attendee).data,
                'check_in_log': CheckInLogSerializer(check_in_log).data
            }, status=status.HTTP_200_OK)
            
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error en check-in: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def my_attendances(self, request):
        """
        Obtener asistencias del usuario autenticado.
        """
        attendees = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(attendees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_event(self, request):
        """
        Obtener asistentes por evento.
        """
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {'error': 'Se requiere event_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendees = self.queryset.filter(event_id=event_id)
        serializer = self.get_serializer(attendees, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Exportar asistentes a CSV.
        """
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {'error': 'Se requiere event_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar permisos (debe ser organizador del evento)
        attendees = self.queryset.filter(event_id=event_id)
        
        if not attendees.exists():
            return Response(
                {'error': 'No hay asistentes para exportar'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Crear respuesta CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendees_event_{event_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Evento', 'Nombre', 'Email', 'Teléfono',
            'Tipo Documento', 'Número Documento', 'Código Ticket',
            'Tipo Ticket', 'Estado', 'Check-in', 'Número de Check-ins',
            'Requerimientos Especiales', 'Restricciones Alimentarias'
        ])
        
        for attendee in attendees:
            writer.writerow([
                attendee.id,
                attendee.event.title,
                attendee.full_name,
                attendee.email,
                attendee.phone,
                attendee.document_type,
                attendee.document_number,
                attendee.ticket.code,
                attendee.ticket.ticket_type.name,
                attendee.status,
                attendee.checked_in_at.strftime('%Y-%m-%d %H:%M') if attendee.checked_in_at else '',
                attendee.total_check_ins,
                attendee.special_requirements,
                attendee.dietary_restrictions
            ])
        
        return response

    def get_client_ip(self, request):
        """Obtener IP del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SurveyViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de encuestas.
    
    list: Listar encuestas
    retrieve: Obtener detalle de encuesta
    create: Crear encuesta
    update: Actualizar encuesta
    destroy: Eliminar encuesta
    submit_responses: Enviar respuestas
    results: Ver resultados
    statistics: Ver estadísticas
    """
    queryset = Survey.objects.select_related('event', 'created_by').all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date']
    filterset_fields = ['event', 'status', 'is_anonymous']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurveyDetailSerializer
        elif self.action == 'submit_responses':
            return SubmitSurveySerializer
        return SurveySerializer

    def perform_create(self, serializer):
        """Asignar creador automáticamente."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def submit_responses(self, request, pk=None):
        """
        Enviar respuestas a una encuesta.
        """
        survey = self.get_object()
        serializer = SubmitSurveySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        responses_data = serializer.validated_data['responses']
        user = request.user
        
        # Verificar si ya respondió (si no permite múltiples respuestas)
        if not survey.allow_multiple_responses:
            existing = SurveyResponse.objects.filter(
                question__survey=survey,
                respondent=user
            ).exists()
            
            if existing:
                return Response(
                    {'error': 'Ya has respondido esta encuesta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Obtener asistente si existe
        try:
            attendee = Attendee.objects.get(user=user, event=survey.event)
        except Attendee.DoesNotExist:
            attendee = None
        
        # Crear respuestas
        created_responses = []
        for response_data in responses_data:
            question_id = response_data['question_id']
            
            try:
                question = SurveyQuestion.objects.get(id=question_id, survey=survey)
            except SurveyQuestion.DoesNotExist:
                continue
            
            response_obj = SurveyResponse.objects.create(
                question=question,
                respondent=user if not survey.is_anonymous else None,
                attendee=attendee,
                text_response=response_data.get('text_response', ''),
                rating_response=response_data.get('rating_response'),
                choice_response=response_data.get('choice_response')
            )
            created_responses.append(response_obj)
        
        return Response({
            'message': 'Respuestas enviadas exitosamente',
            'responses_count': len(created_responses)
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """
        Ver resultados de la encuesta.
        """
        survey = self.get_object()
        
        # Solo el organizador puede ver resultados
        if survey.event.organizer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'No tienes permiso para ver estos resultados'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        results = []
        for question in survey.questions.all():
            question_results = {
                'question': SurveyQuestionSerializer(question).data,
                'total_responses': question.responses.count()
            }
            
            if question.question_type == 'rating':
                # Calcular promedio de calificación
                ratings = question.responses.filter(
                    rating_response__isnull=False
                ).values_list('rating_response', flat=True)
                
                if ratings:
                    question_results['average_rating'] = sum(ratings) / len(ratings)
                    question_results['rating_distribution'] = {
                        i: list(ratings).count(i) for i in range(1, 6)
                    }
            
            elif question.question_type in ['multiple_choice', 'yes_no']:
                # Contar respuestas por opción
                responses = question.responses.all()
                choice_counts = {}
                
                for response in responses:
                    choice = response.choice_response
                    if choice:
                        choice_counts[str(choice)] = choice_counts.get(str(choice), 0) + 1
                
                question_results['choice_distribution'] = choice_counts
            
            results.append(question_results)
        
        return Response({
            'survey': SurveySerializer(survey).data,
            'results': results
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Ver estadísticas de la encuesta.
        """
        survey = self.get_object()
        
        return Response({
            'total_responses': survey.total_responses,
            'response_rate': survey.response_rate,
            'is_active': survey.is_active,
            'questions_count': survey.questions.count(),
            'start_date': survey.start_date,
            'end_date': survey.end_date
        })