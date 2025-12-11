"""
Comando para enviar recordatorios de eventos.
Ejecutar: python manage.py send_event_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.tickets.models import Ticket
from core.emails import EmailService


class Command(BaseCommand):
    help = 'Envía recordatorios de eventos próximos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Días de anticipación para el recordatorio (default: 1)'
        )

    def handle(self, *args, **options):
        days_before = options['days']
        target_date = timezone.now() + timedelta(days=days_before)
        
        # Buscar eventos en la fecha objetivo
        tickets = Ticket.objects.filter(
            status='active',
            ticket_type__event__start_date__date=target_date.date()
        ).select_related('ticket_type__event', 'buyer')
        
        sent_count = 0
        error_count = 0
        
        for ticket in tickets:
            try:
                if EmailService.send_event_reminder(ticket, days_before):
                    sent_count += 1
                else:
                    error_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error con ticket {ticket.code}: {str(e)}')
                )
                error_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Recordatorios enviados: {sent_count}\n'
                f'❌ Errores: {error_count}'
            )
        )