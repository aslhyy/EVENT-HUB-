"""
Modelos para la gestión de tickets y ventas.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.events.models import Event
from core.utils import generate_ticket_code, generate_qr_code
import uuid


class TicketType(models.Model):
    """
    Tipos de tickets para un evento (VIP, General, Estudiante, etc.)
    """
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='ticket_types',
        verbose_name="Evento"
    )
    name = models.CharField(max_length=100, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Precio"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad Total"
    )
    sold_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad Vendida"
    )
    max_purchase = models.PositiveIntegerField(
        default=10,
        verbose_name="Máximo por compra"
    )
    min_purchase = models.PositiveIntegerField(
        default=1,
        verbose_name="Mínimo por compra"
    )
    sale_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de Venta"
    )
    sale_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de Venta"
    )
    is_active = models.BooleanField(default=True, verbose_name="¿Activo?")
    benefits = models.TextField(
        blank=True,
        verbose_name="Beneficios",
        help_text="Separados por comas"
    )
    color = models.CharField(
        max_length=7,
        default="#3498db",
        verbose_name="Color"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tipo de Ticket"
        verbose_name_plural = "Tipos de Tickets"
        ordering = ['price']
        unique_together = ['event', 'name']

    def __str__(self):
        return f"{self.event.title} - {self.name}"

    @property
    def available_quantity(self):
        """Retorna la cantidad disponible."""
        return self.quantity - self.sold_count

    @property
    def is_available(self):
        """Verifica si hay tickets disponibles."""
        now = timezone.now()
        
        # Verificar si está activo
        if not self.is_active:
            return False
        
        # Verificar cantidad
        if self.available_quantity <= 0:
            return False
        
        # Verificar fechas de venta
        if self.sale_start and now < self.sale_start:
            return False
        
        if self.sale_end and now > self.sale_end:
            return False
        
        return True

    @property
    def sold_out(self):
        """Verifica si está agotado."""
        return self.sold_count >= self.quantity

    @property
    def percentage_sold(self):
        """Retorna el porcentaje vendido."""
        if self.quantity == 0:
            return 0
        return (self.sold_count / self.quantity) * 100

    def get_benefit_list(self):
        """Retorna lista de beneficios."""
        return [benefit.strip() for benefit in self.benefits.split(',') if benefit.strip()]


class Ticket(models.Model):
    """
    Tickets individuales comprados por usuarios.
    """
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('used', 'Usado'),
        ('cancelled', 'Cancelado'),
        ('expired', 'Expirado'),
    ]

    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name="Tipo de Ticket"
    )
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchased_tickets',
        verbose_name="Comprador"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código",
        editable=False
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="UUID"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Estado"
    )
    
    # Información del asistente
    attendee_name = models.CharField(max_length=200, verbose_name="Nombre del Asistente")
    attendee_email = models.EmailField(verbose_name="Email del Asistente")
    attendee_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono del Asistente"
    )
    
    # Información de pago
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Precio de Compra"
    )
    discount_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Descuento Aplicado"
    )
    discount_code = models.ForeignKey(
        'DiscountCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name="Código de Descuento"
    )
    
    # QR y PDF
    qr_code = models.ImageField(
        upload_to='tickets/qr/',
        blank=True,
        null=True,
        verbose_name="Código QR"
    )
    pdf_ticket = models.FileField(
        upload_to='tickets/pdf/',
        blank=True,
        null=True,
        verbose_name="Ticket PDF"
    )
    
    # Fechas
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Compra")
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Uso"
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Cancelación"
    )
    
    # Notas
    notes = models.TextField(blank=True, verbose_name="Notas")

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status', 'ticket_type']),
            models.Index(fields=['buyer', 'status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.ticket_type.name}"

    def save(self, *args, **kwargs):
        """Generate code and QR on creation."""
        if not self.code:
            self.code = generate_ticket_code()
            
            # Asegurar que el código es único
            while Ticket.objects.filter(code=self.code).exists():
                self.code = generate_ticket_code()
        
        # Establecer precio de compra si no está establecido
        if not self.purchase_price:
            self.purchase_price = self.ticket_type.price
        
        super().save(*args, **kwargs)
        
        # Generar QR code si no existe
        if not self.qr_code:
            qr_data = f"{self.uuid}"
            self.qr_code = generate_qr_code(qr_data)
            super().save(update_fields=['qr_code'])

    @property
    def final_price(self):
        """Retorna el precio final después del descuento."""
        return self.purchase_price - self.discount_applied

    @property
    def is_valid(self):
        """Verifica si el ticket es válido."""
        return self.status == 'active'

    @property
    def can_be_cancelled(self):
        """Verifica si el ticket puede ser cancelado."""
        if self.status != 'active':
            return False
        
        # No se puede cancelar si el evento ya pasó
        if self.ticket_type.event.is_past:
            return False
        
        # No se puede cancelar si falta menos de 24 horas
        hours_until_event = (self.ticket_type.event.start_date - timezone.now()).total_seconds() / 3600
        return hours_until_event > 24


class DiscountCode(models.Model):
    """
    Códigos de descuento para tickets.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='discount_codes',
        verbose_name="Evento"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Código"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        verbose_name="Tipo de Descuento"
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Valor del Descuento"
    )
    
    # Límites
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Usos Máximos"
    )
    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Veces Usado"
    )
    max_uses_per_user = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Usos Máximos por Usuario"
    )
    
    # Fechas
    valid_from = models.DateTimeField(verbose_name="Válido Desde")
    valid_until = models.DateTimeField(verbose_name="Válido Hasta")
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="¿Activo?")
    minimum_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Compra Mínima"
    )
    
    # Tipos de ticket aplicables
    applicable_ticket_types = models.ManyToManyField(
        TicketType,
        blank=True,
        related_name='discount_codes',
        verbose_name="Tipos de Ticket Aplicables"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Código de Descuento"
        verbose_name_plural = "Códigos de Descuento"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.event.title}"

    @property
    def is_valid(self):
        """Verifica si el código es válido."""
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        
        return True

    @property
    def remaining_uses(self):
        """Retorna los usos restantes."""
        if not self.max_uses:
            return None
        return max(0, self.max_uses - self.used_count)

    def calculate_discount(self, original_price):
        """
        Calcula el monto del descuento.
        
        Args:
            original_price: Precio original del ticket
            
        Returns:
            Monto del descuento
        """
        if self.discount_type == 'percentage':
            discount = (original_price * self.discount_value) / 100
        else:  # fixed
            discount = self.discount_value
        
        # El descuento no puede ser mayor al precio
        return min(discount, original_price)

    def can_be_used_by_user(self, user):
        """
        Verifica si el código puede ser usado por un usuario.
        
        Args:
            user: Usuario que intenta usar el código
            
        Returns:
            Boolean indicando si puede usarlo
        """
        if not self.is_valid:
            return False
        
        # Contar usos del usuario
        user_uses = Ticket.objects.filter(
            discount_code=self,
            buyer=user
        ).count()
        
        return user_uses < self.max_uses_per_user