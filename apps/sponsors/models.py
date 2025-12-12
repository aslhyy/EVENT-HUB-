"""
Modelos para la gestión de patrocinadores.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.events.models import Event


class SponsorTier(models.Model):
    """
    Niveles de patrocinio (Platinum, Gold, Silver, Bronze, etc.)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    min_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Mínimo"
    )
    max_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Monto Máximo"
    )
    color = models.CharField(
        max_length=7,
        default="#FFD700",
        verbose_name="Color"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icono"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden"
    )
    benefits_description = models.TextField(
        blank=True,
        verbose_name="Descripción de Beneficios"
    )
    is_active = models.BooleanField(default=True, verbose_name="¿Activo?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nivel de Patrocinio"
        verbose_name_plural = "Niveles de Patrocinio"
        ordering = ['order', '-min_amount']

    def __str__(self):
        return self.name

    @property
    def sponsors_count(self):
        """Retorna el número de patrocinadores en este nivel."""
        return self.sponsorships.filter(status='active').count()

    @property
    def active_sponsorships_count(self):
        """Retorna el número de patrocinios activos en este nivel."""
        return Sponsorship.objects.filter(
            sponsor_tier=self,
            is_active=True
        ).count()


class Sponsor(models.Model):
    """
    Empresas u organizaciones patrocinadoras.
    """
    STATUS_CHOICES = [
        ('prospect', 'Prospecto'),
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('blacklisted', 'Lista Negra'),
    ]

    # Información básica
    name = models.CharField(max_length=200, verbose_name="Nombre")
    logo = models.ImageField(
        upload_to='sponsors/logos/',
        blank=True,
        null=True,
        verbose_name="Logo"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    industry = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Industria"
    )
    
    # Contacto
    contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre de Contacto"
    )
    contact_email = models.EmailField(verbose_name="Email de Contacto")
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto"
    )
    contact_position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cargo del Contacto"
    )
    
    # Redes sociales y web
    website = models.URLField(blank=True, verbose_name="Sitio Web")
    facebook = models.CharField(max_length=200, blank=True, verbose_name="Facebook")
    twitter = models.CharField(max_length=200, blank=True, verbose_name="Twitter")
    instagram = models.CharField(max_length=200, blank=True, verbose_name="Instagram")
    linkedin = models.CharField(max_length=200, blank=True, verbose_name="LinkedIn")
    
    # Información fiscal
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="NIT/RUT"
    )
    billing_address = models.TextField(
        blank=True,
        verbose_name="Dirección de Facturación"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='prospect',
        verbose_name="Estado"
    )
    
    # Metadata
    notes = models.TextField(blank=True, verbose_name="Notas")
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Etiquetas",
        help_text="Separadas por comas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Patrocinador"
        verbose_name_plural = "Patrocinadores"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_sponsorships(self):
        """Retorna el número total de patrocinios."""
        return self.sponsorships.count()

    @property
    def active_sponsorships(self):
        """Retorna patrocinios activos."""
        return self.sponsorships.filter(is_active=True)

    @property
    def total_invested(self):
        """Retorna el monto total invertido."""
        return self.sponsorships.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    def get_tag_list(self):
        """Retorna lista de tags."""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class Sponsorship(models.Model):
    """
    Relación entre patrocinador y evento.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='sponsorships',
        verbose_name="Evento"
    )
    sponsor = models.ForeignKey(
        Sponsor,
        on_delete=models.CASCADE,
        related_name='sponsorships',
        verbose_name="Patrocinador"
    )
    sponsor_tier = models.ForeignKey(
        SponsorTier,
        on_delete=models.PROTECT,
        related_name='sponsorships',
        verbose_name="Nivel de Patrocinio"
    )
    
    # Financiero
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Monto"
    )
    currency = models.CharField(
        max_length=3,
        default='COP',
        verbose_name="Moneda"
    )
    
    # Estado
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Estado"
    )
    is_active = models.BooleanField(default=True, verbose_name="¿Activo?")
    
    # Fechas
    start_date = models.DateField(verbose_name="Fecha de Inicio")
    end_date = models.DateField(verbose_name="Fecha de Fin")
    contract_signed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Firma de Contrato"
    )
    
    # Documentos
    contract_document = models.FileField(
        upload_to='sponsorships/contracts/',
        blank=True,
        null=True,
        verbose_name="Documento de Contrato"
    )
    
    # Visibilidad
    logo_placement = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Ubicación del Logo",
        help_text="Dónde se mostrará el logo del patrocinador"
    )
    booth_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Número de Stand"
    )
    
    # Métricas
    impressions = models.PositiveIntegerField(
        default=0,
        verbose_name="Impresiones"
    )
    clicks = models.PositiveIntegerField(
        default=0,
        verbose_name="Clicks"
    )
    leads_generated = models.PositiveIntegerField(
        default=0,
        verbose_name="Leads Generados"
    )
    
    # Notas
    notes = models.TextField(blank=True, verbose_name="Notas")
    internal_notes = models.TextField(
        blank=True,
        verbose_name="Notas Internas"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Patrocinio"
        verbose_name_plural = "Patrocinios"
        ordering = ['-created_at']
        unique_together = ['event', 'sponsor']

    def __str__(self):
        return f"{self.sponsor.name} - {self.event.title}"

    @property
    def is_current(self):
        """Verifica si el patrocinio está vigente."""
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    @property
    def days_remaining(self):
        """Retorna días restantes del patrocinio."""
        if not self.is_current:
            return 0
        today = timezone.now().date()
        return (self.end_date - today).days

    @property
    def roi_metrics(self):
        """Calcula métricas de ROI."""
        if self.amount == 0:
            return {}
        
        return {
            'impressions': self.impressions,
            'clicks': self.clicks,
            'leads': self.leads_generated,
            'cpl': float(self.amount / self.leads_generated) if self.leads_generated > 0 else 0,
            'ctr': (self.clicks / self.impressions * 100) if self.impressions > 0 else 0
        }

    @property
    def benefits_delivered_count(self):
        """Retorna el número de beneficios entregados."""
        return self.benefits.filter(delivered=True).count()

    @property
    def benefits_pending_count(self):
        """Retorna el número de beneficios pendientes."""
        return self.benefits.filter(delivered=False).count()


class SponsorBenefit(models.Model):
    """
    Beneficios específicos entregados a patrocinadores.
    """
    BENEFIT_TYPE_CHOICES = [
        ('logo_placement', 'Ubicación de Logo'),
        ('booth_space', 'Espacio de Stand'),
        ('tickets', 'Tickets Gratuitos'),
        ('social_media', 'Mención en Redes Sociales'),
        ('email_blast', 'Email a Asistentes'),
        ('speaking_slot', 'Espacio para Charla'),
        ('branding', 'Branding en Evento'),
        ('other', 'Otro'),
    ]

    sponsorship = models.ForeignKey(
        Sponsorship,
        on_delete=models.CASCADE,
        related_name='benefits',
        verbose_name="Patrocinio"
    )
    benefit_type = models.CharField(
        max_length=50,
        choices=BENEFIT_TYPE_CHOICES,
        verbose_name="Tipo de Beneficio"
    )
    description = models.TextField(verbose_name="Descripción")
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad"
    )
    delivered = models.BooleanField(
        default=False,
        verbose_name="¿Entregado?"
    )
    delivered_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Entrega"
    )
    proof_of_delivery = models.FileField(
        upload_to='sponsorships/benefits/',
        blank=True,
        null=True,
        verbose_name="Comprobante de Entrega"
    )
    notes = models.TextField(blank=True, verbose_name="Notas")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Beneficio de Patrocinio"
        verbose_name_plural = "Beneficios de Patrocinio"
        ordering = ['sponsorship', 'benefit_type']

    def __str__(self):
        return f"{self.get_benefit_type_display()} - {self.sponsorship.sponsor.name}"

    def mark_as_delivered(self):
        """Marcar beneficio como entregado."""
        self.delivered = True
        self.delivered_date = timezone.now().date()
        self.save()