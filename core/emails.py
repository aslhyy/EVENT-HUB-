"""
Sistema de envío de emails para EventHub.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio centralizado para envío de emails."""
    
    @staticmethod
    def send_email(subject, to_email, template_name, context, from_email=None):
        """
        Enviar email con template HTML.
        
        Args:
            subject: Asunto del email
            to_email: Email destino (puede ser lista)
            template_name: Nombre del template (sin .html)
            context: Contexto para el template
            from_email: Email remitente (opcional)
        """
        try:
            # Preparar email
            from_email = from_email or settings.DEFAULT_FROM_EMAIL
            to_email = [to_email] if isinstance(to_email, str) else to_email
            
            # Renderizar templates
            html_content = render_to_string(f'emails/{template_name}.html', context)
            text_content = strip_tags(html_content)
            
            # Crear email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=to_email
            )
            email.attach_alternative(html_content, "text/html")
            
            # Enviar
            email.send(fail_silently=False)
            logger.info(f"Email enviado a {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_ticket_purchase_confirmation(ticket):
        """Enviar confirmación de compra de ticket."""
        context = {
            'ticket': ticket,
            'event': ticket.ticket_type.event,
            'buyer_name': ticket.buyer.get_full_name() or ticket.buyer.username,
            'qr_code_url': ticket.qr_code.url if ticket.qr_code else None,
            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        return EmailService.send_email(
            subject=f'Confirmación de compra - {ticket.ticket_type.event.title}',
            to_email=ticket.attendee_email,
            template_name='ticket_purchase_confirmation',
            context=context
        )
    
    @staticmethod
    def send_event_reminder(ticket, days_before):
        """Enviar recordatorio de evento."""
        context = {
            'ticket': ticket,
            'event': ticket.ticket_type.event,
            'attendee_name': ticket.attendee_name,
            'days_before': days_before,
            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        return EmailService.send_email(
            subject=f'Recordatorio: {ticket.ticket_type.event.title} en {days_before} días',
            to_email=ticket.attendee_email,
            template_name='event_reminder',
            context=context
        )
    
    @staticmethod
    def send_event_cancelled(event):
        """Enviar notificación de evento cancelado."""
        # Obtener todos los tickets activos
        from apps.tickets.models import Ticket
        tickets = Ticket.objects.filter(
            ticket_type__event=event,
            status='active'
        ).select_related('buyer')
        
        for ticket in tickets:
            context = {
                'ticket': ticket,
                'event': event,
                'attendee_name': ticket.attendee_name,
                'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
            }
            
            EmailService.send_email(
                subject=f'CANCELADO: {event.title}',
                to_email=ticket.attendee_email,
                template_name='event_cancelled',
                context=context
            )
    
    @staticmethod
    def send_check_in_confirmation(attendee):
        """Enviar confirmación de check-in."""
        context = {
            'attendee': attendee,
            'event': attendee.event,
            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        return EmailService.send_email(
            subject=f'Check-in confirmado - {attendee.event.title}',
            to_email=attendee.email,
            template_name='check_in_confirmation',
            context=context
        )
    
    @staticmethod
    def send_survey_invitation(attendee, survey):
        """Enviar invitación a encuesta."""
        context = {
            'attendee': attendee,
            'survey': survey,
            'event': survey.event,
            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        return EmailService.send_email(
            subject=f'Tu opinión importa - {survey.event.title}',
            to_email=attendee.email,
            template_name='survey_invitation',
            context=context
        )
    
    @staticmethod
    def send_sponsorship_proposal(sponsorship):
        """Enviar propuesta de patrocinio."""
        context = {
            'sponsorship': sponsorship,
            'sponsor': sponsorship.sponsor,
            'event': sponsorship.event,
            'frontend_url': settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else '#'
        }
        
        return EmailService.send_email(
            subject=f'Propuesta de Patrocinio - {sponsorship.event.title}',
            to_email=sponsorship.sponsor.contact_email,
            template_name='sponsorship_proposal',
            context=context
        )