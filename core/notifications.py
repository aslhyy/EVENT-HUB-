"""
Sistema de notificaciones en tiempo real.
"""
from channels.layers import get_channel_layer # type: ignore
from asgiref.sync import async_to_sync


class NotificationService:
    """Servicio para enviar notificaciones en tiempo real."""
    
    @staticmethod
    def send_notification(user_id, notification_type, data):
        """
        Enviar notificación a un usuario específico.
        """
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    'type': 'notification_message',
                    'notification_type': notification_type,
                    'data': data
                }
            )
    
    @staticmethod
    def notify_new_ticket_purchase(ticket):
        """Notificar al organizador sobre nueva compra."""
        NotificationService.send_notification(
            user_id=ticket.ticket_type.event.organizer.id,
            notification_type='new_purchase',
            data={
                'message': f'Nueva compra para {ticket.ticket_type.event.title}',
                'ticket_code': ticket.code,
                'buyer': ticket.buyer.username,
                'amount': float(ticket.final_price)
            }
        )
    
    @staticmethod
    def notify_event_update(event):
        """Notificar a asistentes sobre actualización del evento."""
        from apps.tickets.models import Ticket
        tickets = Ticket.objects.filter(
            ticket_type__event=event,
            status='active'
        ).values_list('buyer_id', flat=True).distinct()
        
        for user_id in tickets:
            NotificationService.send_notification(
                user_id=user_id,
                notification_type='event_update',
                data={
                    'message': f'Actualización en {event.title}',
                    'event_id': event.id,
                    'event_title': event.title
                }
            )