"""
Views para patrocinadores.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db import transaction
from django.db.models import Sum, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import SponsorTier, Sponsor, Sponsorship, SponsorBenefit
from .serializers import (
    SponsorTierSerializer, SponsorSerializer, SponsorDetailSerializer,
    SponsorshipSerializer, SponsorshipDetailSerializer,
    SponsorshipCreateUpdateSerializer, SponsorBenefitSerializer,
    SponsorshipROISerializer
)
from .filters import SponsorFilter, SponsorshipFilter
from core.permissions import IsEventOrganizer, IsAdminOrReadOnly


class SponsorTierViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de niveles de patrocinio.
    
    list: Listar niveles
    retrieve: Obtener detalle de nivel
    create: Crear nivel (solo admin)
    update: Actualizar nivel (solo admin)
    destroy: Eliminar nivel (solo admin)
    """
    queryset = SponsorTier.objects.all()
    serializer_class = SponsorTierSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'min_amount', 'created_at']


class SponsorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de patrocinadores.
    
    list: Listar patrocinadores
    retrieve: Obtener detalle de patrocinador
    create: Crear patrocinador
    update: Actualizar patrocinador
    destroy: Eliminar patrocinador
    history: Historial de patrocinios
    roi_report: Reporte de ROI
    statistics: Estadísticas del patrocinador
    """
    queryset = Sponsor.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SponsorFilter
    search_fields = ['name', 'industry', 'contact_name', 'contact_email']
    ordering_fields = ['name', 'created_at', 'total_invested']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SponsorDetailSerializer
        return SponsorSerializer

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """
        Obtener historial de patrocinios del sponsor.
        """
        sponsor = self.get_object()
        sponsorships = sponsor.sponsorships.all().order_by('-start_date')
        serializer = SponsorshipSerializer(sponsorships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def roi_report(self, request, pk=None):
        """
        Generar reporte de ROI del patrocinador.
        """
        sponsor = self.get_object()
        sponsorships = sponsor.sponsorships.filter(status='completed')
        
        report_data = []
        for sponsorship in sponsorships:
            roi_data = {
                'sponsorship_id': sponsorship.id,
                'sponsor_name': sponsor.name,
                'event_title': sponsorship.event.title,
                'amount': sponsorship.amount,
                'impressions': sponsorship.impressions,
                'clicks': sponsorship.clicks,
                'leads_generated': sponsorship.leads_generated,
                'cpl': sponsorship.roi_metrics.get('cpl', 0),
                'ctr': sponsorship.roi_metrics.get('ctr', 0),
                'roi_score': (
                    (sponsorship.leads_generated * 100) / float(sponsorship.amount)
                    if sponsorship.amount > 0 else 0
                )
            }
            report_data.append(roi_data)
        
        serializer = SponsorshipROISerializer(report_data, many=True)
        return Response({
            'sponsor': SponsorSerializer(sponsor).data,
            'total_investment': sponsor.total_invested,
            'total_sponsorships': len(report_data),
            'roi_details': serializer.data
        })

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Obtener estadísticas del patrocinador.
        """
        sponsor = self.get_object()
        
        stats = {
            'total_sponsorships': sponsor.total_sponsorships,
            'active_sponsorships': sponsor.active_sponsorships.count(),
            'total_invested': sponsor.total_invested,
            'total_impressions': sponsor.sponsorships.aggregate(
                total=Sum('impressions')
            )['total'] or 0,
            'total_clicks': sponsor.sponsorships.aggregate(
                total=Sum('clicks')
            )['total'] or 0,
            'total_leads': sponsor.sponsorships.aggregate(
                total=Sum('leads_generated')
            )['total'] or 0,
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Obtener patrocinadores activos.
        """
        sponsors = self.queryset.filter(status='active')
        serializer = self.get_serializer(sponsors, many=True)
        return Response(serializer.data)


class SponsorshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de patrocinios.
    
    list: Listar patrocinios
    retrieve: Obtener detalle de patrocinio
    create: Crear patrocinio
    update: Actualizar patrocinio
    destroy: Eliminar patrocinio
    activate: Activar patrocinio
    deactivate: Desactivar patrocinio
    mark_benefit_delivered: Marcar beneficio como entregado
    exposure_report: Reporte de exposición
    """
    queryset = Sponsorship.objects.select_related(
        'event', 'sponsor', 'sponsor_tier'
    ).all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SponsorshipFilter
    search_fields = ['sponsor__name', 'event__title']
    ordering_fields = ['amount', 'start_date', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SponsorshipDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SponsorshipCreateUpdateSerializer
        return SponsorshipSerializer

    def get_permissions(self):
        """Permisos según la acción."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsEventOrganizer()]
        return super().get_permissions()

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activar un patrocinio.
        """
        sponsorship = self.get_object()
        
        if sponsorship.is_active:
            return Response(
                {'error': 'El patrocinio ya está activo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sponsorship.is_active = True
        sponsorship.status = 'active'
        sponsorship.save()
        
        serializer = self.get_serializer(sponsorship)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactivar un patrocinio.
        """
        sponsorship = self.get_object()
        
        if not sponsorship.is_active:
            return Response(
                {'error': 'El patrocinio ya está inactivo'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sponsorship.is_active = False
        sponsorship.save()
        
        serializer = self.get_serializer(sponsorship)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    @transaction.atomic
    def mark_benefit_delivered(self, request, pk=None):
        """
        Marcar un beneficio como entregado.
        """
        sponsorship = self.get_object()
        benefit_id = request.data.get('benefit_id')
        
        if not benefit_id:
            return Response(
                {'error': 'Se requiere benefit_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            benefit = SponsorBenefit.objects.get(
                id=benefit_id,
                sponsorship=sponsorship
            )
            benefit.mark_as_delivered()
            
            return Response({
                'message': 'Beneficio marcado como entregado',
                'benefit': SponsorBenefitSerializer(benefit).data
            })
            
        except SponsorBenefit.DoesNotExist:
            return Response(
                {'error': 'Beneficio no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def exposure_report(self, request, pk=None):
        """
        Generar reporte de exposición del patrocinio.
        """
        sponsorship = self.get_object()
        
        report = {
            'sponsorship': SponsorshipSerializer(sponsorship).data,
            'metrics': {
                'impressions': sponsorship.impressions,
                'clicks': sponsorship.clicks,
                'leads_generated': sponsorship.leads_generated,
                'ctr': sponsorship.roi_metrics.get('ctr', 0),
                'cpl': sponsorship.roi_metrics.get('cpl', 0),
            },
            'benefits': {
                'total': sponsorship.benefits.count(),
                'delivered': sponsorship.benefits_delivered_count,
                'pending': sponsorship.benefits_pending_count,
            },
            'duration': {
                'start_date': sponsorship.start_date,
                'end_date': sponsorship.end_date,
                'is_current': sponsorship.is_current,
                'days_remaining': sponsorship.days_remaining,
            }
        }
        
        return Response(report)

    @action(detail=False, methods=['get'])
    def by_event(self, request):
        """
        Obtener patrocinios por evento.
        """
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {'error': 'Se requiere event_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sponsorships = self.queryset.filter(event_id=event_id, is_active=True)
        serializer = self.get_serializer(sponsorships, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Obtener patrocinios activos.
        """
        sponsorships = self.queryset.filter(is_active=True, status='active')
        serializer = self.get_serializer(sponsorships, many=True)
        return Response(serializer.data)


class SponsorBenefitViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de beneficios de patrocinio.
    
    list: Listar beneficios
    retrieve: Obtener detalle de beneficio
    create: Crear beneficio
    update: Actualizar beneficio
    destroy: Eliminar beneficio
    mark_delivered: Marcar como entregado
    """
    queryset = SponsorBenefit.objects.select_related('sponsorship').all()
    serializer_class = SponsorBenefitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['description', 'benefit_type']
    ordering_fields = ['created_at', 'delivered_date']
    filterset_fields = ['sponsorship', 'benefit_type', 'delivered']

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """
        Marcar beneficio como entregado.
        """
        benefit = self.get_object()
        benefit.mark_as_delivered()
        
        serializer = self.get_serializer(benefit)
        return Response({
            'message': 'Beneficio marcado como entregado',
            'benefit': serializer.data
        })

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Obtener beneficios pendientes.
        """
        benefits = self.queryset.filter(delivered=False)
        serializer = self.get_serializer(benefits, many=True)
        return Response(serializer.data)