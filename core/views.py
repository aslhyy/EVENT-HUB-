"""
Vistas generales del sistema.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from apps.events.models import Event
from apps.tickets.models import Ticket, TicketType
from apps.attendees.models import Attendee
from apps.sponsors.models import Sponsorship

from datetime import timedelta, datetime
from django.utils import timezone



@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Endpoint de health check para verificar el estado del servicio.
    
    Returns:
        Response con el estado del servicio y la base de datos.
    """
    health_status = {
        'status': 'healthy',
        'service': 'EventHub API',
        'version': '1.0.0',
    }
    
    # Verificar conexión a la base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['database'] = 'connected'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['database'] = f'disconnected: {str(e)}'
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    return Response(health_status, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Dashboard con estadísticas generales del sistema.
    """
    user = request.user
    
    # Estadísticas de eventos
    if user.is_staff:
        events = Event.objects.all()
    else:
        events = Event.objects.filter(organizer=user)
    
    total_events = events.count()
    published_events = events.filter(status='published').count()
    upcoming_events = events.filter(
        status='published',
        start_date__gte=timezone.now()
    ).count()
    
    # Estadísticas de tickets
    tickets = Ticket.objects.filter(
        ticket_type__event__in=events
    )
    total_tickets_sold = tickets.filter(status='active').count()
    total_revenue = tickets.filter(status='active').aggregate(
        total=Sum('final_price')
    )['total'] or 0
    
    # Estadísticas de asistencia
    total_attendees = Attendee.objects.filter(event__in=events).count()
    checked_in = Attendee.objects.filter(
        event__in=events,
        status='checked_in'
    ).count()
    
    # Estadísticas de patrocinios
    total_sponsorships = Sponsorship.objects.filter(
        event__in=events,
        is_active=True
    ).count()
    sponsorship_revenue = Sponsorship.objects.filter(
        event__in=events,
        is_active=True
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Eventos más populares
    popular_events = events.filter(
        status='published'
    ).annotate(
        tickets_count=Count('ticket_types__tickets')
    ).order_by('-tickets_count')[:5]
    
    # Tendencias de ventas (últimos 7 días)
    last_7_days = timezone.now() - timedelta(days=7)
    daily_sales = []
    for i in range(7):
        date = last_7_days + timedelta(days=i)
        sales = tickets.filter(
            purchased_at__date=date.date()
        ).count()
        daily_sales.append({
            'date': date.strftime('%Y-%m-%d'),
            'sales': sales
        })
    
    return Response({
        'events': {
            'total': total_events,
            'published': published_events,
            'upcoming': upcoming_events
        },
        'tickets': {
            'sold': total_tickets_sold,
            'revenue': float(total_revenue)
        },
        'attendees': {
            'total': total_attendees,
            'checked_in': checked_in,
            'check_in_rate': (checked_in / total_attendees * 100) if total_attendees > 0 else 0
        },
        'sponsorships': {
            'total': total_sponsorships,
            'revenue': float(sponsorship_revenue)
        },
        'popular_events': [
            {
                'id': event.id,
                'title': event.title,
                'tickets_sold': event.tickets_count
            }
            for event in popular_events
        ],
        'sales_trend': daily_sales
    })