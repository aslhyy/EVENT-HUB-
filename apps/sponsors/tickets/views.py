"""
Views para tickets.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from core.emails import EmailService

from .models import TicketType, Ticket, DiscountCode
from .serializers import (
    TicketTypeSerializer,
    TicketTypeDetailSerializer,
    TicketSerializer,
    TicketDetailSerializer,
    TicketPurchaseSerializer,
    DiscountCodeSerializer,
    TicketValidationSerializer,
)
from .filters import TicketTypeFilter, TicketFilter
from core.permissions import IsEventOrganizer
from core.utils import generate_ticket_pdf


class TicketTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de tipos de tickets.

    list: Listar todos los tipos de tickets
    retrieve: Obtener detalle de un tipo de ticket
    create: Crear nuevo tipo de ticket
    update: Actualizar tipo de ticket
    destroy: Eliminar tipo de ticket
    check_availability: Verificar disponibilidad
    """

    queryset = TicketType.objects.select_related("event").all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TicketTypeFilter
    search_fields = ["name", "description", "event__title"]
    ordering_fields = ["price", "quantity", "sold_count", "created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketTypeDetailSerializer
        return TicketTypeSerializer

    def get_permissions(self):
        """Permisos según la acción."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsEventOrganizer()]
        return super().get_permissions()

    @action(detail=True, methods=["get"])
    def check_availability(self, request, pk=None):
        """
        Verificar disponibilidad de un tipo de ticket.
        """
        ticket_type = self.get_object()

        return Response(
            {
                "available": ticket_type.is_available,
                "available_quantity": ticket_type.available_quantity,
                "sold_out": ticket_type.sold_out,
                "percentage_sold": ticket_type.percentage_sold,
            }
        )

    @action(detail=False, methods=["get"])
    def by_event(self, request):
        """
        Obtener tipos de tickets por evento.
        """
        event_id = request.query_params.get("event_id")
        if not event_id:
            return Response(
                {"error": "Se requiere event_id"}, status=status.HTTP_400_BAD_REQUEST
            )

        ticket_types = self.queryset.filter(event_id=event_id, is_active=True)
        serializer = self.get_serializer(ticket_types, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de tickets.

    list: Listar todos los tickets del usuario
    retrieve: Obtener detalle de un ticket
    purchase: Comprar tickets
    cancel: Cancelar ticket
    verify: Verificar validez de un ticket
    download_pdf: Descargar PDF del ticket
    my_tickets: Obtener tickets del usuario autenticado
    """

    queryset = Ticket.objects.select_related(
        "ticket_type", "ticket_type__event", "buyer", "discount_code"
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ["code", "attendee_name", "attendee_email"]
    ordering_fields = ["purchased_at", "status"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        elif self.action == "purchase":
            return TicketPurchaseSerializer
        elif self.action == "verify":
            return TicketValidationSerializer
        return TicketSerializer

    def get_queryset(self):
        """Filtrar tickets del usuario (excepto para organizadores)."""
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(buyer=user)

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def purchase(self, request):
        """
        Comprar tickets.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tickets = serializer.save()

            # Generar PDFs para los tickets

            for ticket in tickets:
                try:
                    ticket.pdf_ticket = generate_ticket_pdf(ticket)
                    ticket.save(update_fields=["pdf_ticket"])
                except Exception as e:
                    # Log error pero no fallar la compra
                    print(f"Error generating PDF: {e}")

            response_serializer = TicketSerializer(tickets, many=True)

            return Response(
                {
                    "message": f"Compra exitosa de {len(tickets)} ticket(s)",
                    "tickets": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
               {"error": f"Error en la compra: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tickets = purchase.tickets.all()
        
        for ticket in tickets:
            try:
                EmailService.send_ticket_purchase_confirmation(ticket)
            except Exception as e:
                logger.error(f"Error enviando email de confirmación: {e}")

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def cancel(self, request, pk=None):
        """
        Cancelar un ticket.
        """
        ticket = self.get_object()

        # Verificar que el usuario es el dueño
        if ticket.buyer != request.user and not request.user.is_staff:
            return Response(
                {"error": "No tienes permiso para cancelar este ticket"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Verificar si puede ser cancelado
        if not ticket.can_be_cancelled:
            return Response(
                {"error": "Este ticket no puede ser cancelado"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Cancelar ticket
        ticket.status = "cancelled"
        ticket.cancelled_at = timezone.now()
        ticket.save()

        # Devolver ticket al inventario
        ticket.ticket_type.sold_count -= 1
        ticket.ticket_type.save(update_fields=["sold_count"])

        serializer = self.get_serializer(ticket)
        return Response(
            {"message": "Ticket cancelado exitosamente", "ticket": serializer.data}
        )

    @action(detail=False, methods=["post"])
    def verify(self, request):
        """
        Verificar validez de un ticket.
        """
        serializer = TicketValidationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data.get("code")
        uuid_val = serializer.validated_data.get("uuid")

        try:
            if code:
                ticket = Ticket.objects.get(code=code)
            else:
                ticket = Ticket.objects.get(uuid=uuid_val)

            is_valid = ticket.is_valid

            response_data = {
                "valid": is_valid,
                "ticket": TicketDetailSerializer(ticket).data,
            }

            if not is_valid:
                response_data["reason"] = f"Ticket {ticket.status}"

            return Response(response_data)

        except Ticket.DoesNotExist:
            return Response(
                {"valid": False, "reason": "Ticket no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"])
    def download_pdf(self, request, pk=None):
        """
        Obtener URL de descarga del PDF.
        """
        ticket = self.get_object()

        if not ticket.pdf_ticket:
            # Generar PDF si no existe
            try:
                ticket.pdf_ticket = generate_ticket_pdf(ticket)
                ticket.save(update_fields=["pdf_ticket"])
            except Exception as e:
                return Response(
                    {"error": f"Error generando PDF: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"pdf_url": request.build_absolute_uri(ticket.pdf_ticket.url)})

    @action(detail=False, methods=["get"])
    def my_tickets(self, request):
        """
        Obtener tickets del usuario autenticado.
        """
        tickets = self.queryset.filter(buyer=request.user)
        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """
        Obtener tickets de eventos próximos.
        """
        tickets = self.queryset.filter(
            buyer=request.user,
            status="active",
            ticket_type__event__start_date__gte=timezone.now(),
        ).order_by("ticket_type__event__start_date")

        serializer = self.get_serializer(tickets, many=True)
        return Response(serializer.data)


class DiscountCodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de códigos de descuento.

    list: Listar códigos de descuento
    retrieve: Obtener detalle de un código
    create: Crear nuevo código
    update: Actualizar código
    destroy: Eliminar código
    validate: Validar si un código es válido
    """

    queryset = DiscountCode.objects.select_related("event").all()
    serializer_class = DiscountCodeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["code", "description"]
    ordering_fields = ["created_at", "valid_from", "valid_until"]
    filterset_fields = ["event", "discount_type", "is_active"]

    def get_permissions(self):
        """Solo organizadores pueden crear/modificar códigos."""
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsEventOrganizer()]
        return super().get_permissions()

    @action(detail=False, methods=["post"])
    def validate_code(self, request):
        """
        Validar un código de descuento.
        """
        code = request.data.get("code")
        event_id = request.data.get("event_id")

        if not code or not event_id:
            return Response(
                {"error": "Se requieren code y event_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            discount = DiscountCode.objects.get(code=code.upper(), event_id=event_id)

            is_valid = discount.is_valid
            can_use = discount.can_be_used_by_user(request.user)

            response_data = {
                "valid": is_valid and can_use,
                "discount": self.get_serializer(discount).data,
            }

            if not is_valid:
                response_data["reason"] = "Código no válido o expirado"
            elif not can_use:
                response_data["reason"] = "Has alcanzado el límite de uso"

            return Response(response_data)

        except DiscountCode.DoesNotExist:
            return Response(
                {"valid": False, "reason": "Código no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
