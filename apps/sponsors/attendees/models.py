"""
Modelos para la gestión de asistentes y check-in.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tickets.models import Ticket
from apps.events.models import Event


class Attendee(models.Model):
    """
    Información de asistentes a eventos.
    """
    STATUS_CHOICES = [
        ('registered', 'Registrado'),
        ('checked_in', 'Check-in Realizado'),
        ('no_show', 'No Asistió'),
        ('cancelled', 'Cancelado'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Usuario"
    )
    ticket = models.OneToOneField(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attendee',
        verbose_name="Ticket"
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='attendees',
        verbose_name="Evento"
    )
    
    # Información personal
    full_name = models.CharField(max_length=200, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    document_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Tipo de Documento"
    )
    document_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Número de Documento"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='registered',
        verbose_name="Estado"
    )
    
    # Check-in
    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Check-in"
    )
    checked_in_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checked_in_attendees',
        verbose_name="Check-in Realizado Por"
    )
    
    # Información adicional
    special_requirements = models.TextField(
        blank=True,
        verbose_name="Requerimientos Especiales"
    )
    dietary_restrictions = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Restricciones Alimentarias"
    )
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre de Contacto de Emergencia"
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto de Emergencia"
    )
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asistente"
        verbose_name_plural = "Asistentes"
        ordering = ['-created_at']
        unique_together = ['user', 'event']
        indexes = [
            models.Index(fields=['event', 'status']),
            models.Index(fields=['user', 'event']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    @property
    def is_checked_in(self):
        """Verifica si ya hizo check-in."""
        return self.status == 'checked_in'

    @property
    def can_check_in(self):
        """Verifica si puede hacer check-in."""
        if self.status != 'registered':
            return False
        
        if not self.ticket.is_valid:
            return False
        
        # Verificar que el evento está en curso o próximo
        now = timezone.now()
        event_start = self.event.start_date
        
        # Permitir check-in 2 horas antes del evento
        check_in_window_start = event_start - timezone.timedelta(hours=2)
        
        return check_in_window_start <= now <= self.event.end_date

    @property
    def total_check_ins(self):
        """Retorna el número total de check-ins."""
        return self.check_in_logs.count()


class CheckInLog(models.Model):
    """
    Registro de check-ins (permite múltiples check-ins para eventos de múltiples días).
    """
    attendee = models.ForeignKey(
        Attendee,
        on_delete=models.CASCADE,
        related_name='check_in_logs',
        verbose_name="Asistente"
    )
    checked_in_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de Check-in"
    )
    checked_in_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_check_ins',
        verbose_name="Realizado Por"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación"
    )
    device_info = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Información del Dispositivo"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Registro de Check-in"
        verbose_name_plural = "Registros de Check-in"
        ordering = ['-checked_in_at']

    def __str__(self):
        return f"{self.attendee.full_name} - {self.checked_in_at}"


class Survey(models.Model):
    """
    Encuestas post-evento.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('active', 'Activa'),
        ('closed', 'Cerrada'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='surveys',
        verbose_name="Evento"
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Estado"
    )
    
    # Fechas
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Inicio"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Fin"
    )
    
    # Configuración
    is_anonymous = models.BooleanField(
        default=False,
        verbose_name="¿Es Anónima?"
    )
    allow_multiple_responses = models.BooleanField(
        default=False,
        verbose_name="¿Permitir Múltiples Respuestas?"
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_surveys',
        verbose_name="Creado Por"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Encuesta"
        verbose_name_plural = "Encuestas"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.event.title}"

    @property
    def is_active(self):
        """Verifica si la encuesta está activa."""
        if self.status != 'active':
            return False
        
        now = timezone.now()
        
        if self.start_date and now < self.start_date:
            return False
        
        if self.end_date and now > self.end_date:
            return False
        
        return True

    @property
    def total_responses(self):
        """Retorna el número total de respuestas."""
        return SurveyResponse.objects.filter(
            question__survey=self
        ).values('respondent').distinct().count()

    @property
    def response_rate(self):
        """Calcula la tasa de respuesta."""
        total_attendees = self.event.attendees.filter(status='checked_in').count()
        if total_attendees == 0:
            return 0
        return (self.total_responses / total_attendees) * 100


class SurveyQuestion(models.Model):
    """
    Preguntas de encuestas.
    """
    QUESTION_TYPE_CHOICES = [
        ('text', 'Texto Libre'),
        ('rating', 'Calificación (1-5)'),
        ('yes_no', 'Sí/No'),
        ('multiple_choice', 'Opción Múltiple'),
        ('checkbox', 'Casillas de Verificación'),
    ]

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Encuesta"
    )
    question_text = models.TextField(verbose_name="Texto de la Pregunta")
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        verbose_name="Tipo de Pregunta"
    )
    options = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Opciones",
        help_text="Para preguntas de opción múltiple o checkbox"
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name="¿Es Obligatoria?"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pregunta de Encuesta"
        verbose_name_plural = "Preguntas de Encuesta"
        ordering = ['survey', 'order']

    def __str__(self):
        return f"{self.survey.title} - {self.question_text[:50]}"


class SurveyResponse(models.Model):
    """
    Respuestas a encuestas.
    """
    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Pregunta"
    )
    respondent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='survey_responses',
        null=True,
        blank=True,
        verbose_name="Respondiente"
    )
    attendee = models.ForeignKey(
        Attendee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses',
        verbose_name="Asistente"
    )
    
    # Respuesta
    text_response = models.TextField(
        blank=True,
        verbose_name="Respuesta de Texto"
    )
    rating_response = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Calificación"
    )
    choice_response = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Respuesta de Selección"
    )
    
    responded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Respuesta de Encuesta"
        verbose_name_plural = "Respuestas de Encuesta"
        ordering = ['-responded_at']

    def __str__(self):
        respondent_name = self.respondent.username if self.respondent else "Anónimo"
        return f"{respondent_name} - {self.question.question_text[:30]}"