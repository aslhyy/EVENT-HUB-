"""
Modelos para la gestión de eventos.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Category(models.Model):
    """
    Categorías de eventos (Concierto, Conferencia, Deportes, etc.)
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icono")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def events_count(self):
        """Retorna el número de eventos en esta categoría."""
        return self.events.filter(status='published').count()


class Venue(models.Model):
    """
    Lugares donde se realizan los eventos.
    """
    name = models.CharField(max_length=200, verbose_name="Nombre")
    address = models.CharField(max_length=300, verbose_name="Dirección")
    city = models.CharField(max_length=100, verbose_name="Ciudad")
    state = models.CharField(max_length=100, verbose_name="Departamento/Estado")
    country = models.CharField(max_length=100, default="Colombia", verbose_name="País")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Código Postal")
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Capacidad"
    )
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Latitud"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        verbose_name="Longitud"
    )
    description = models.TextField(blank=True, verbose_name="Descripción")
    amenities = models.TextField(blank=True, verbose_name="Amenidades", help_text="Separadas por comas")
    image = models.ImageField(upload_to='venues/', blank=True, null=True, verbose_name="Imagen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lugar"
        verbose_name_plural = "Lugares"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city}"

    @property
    def full_address(self):
        """Retorna la dirección completa."""
        return f"{self.address}, {self.city}, {self.state}, {self.country}"


class Event(models.Model):
    """
    Modelo principal de eventos.
    """
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
        ('ongoing', 'En Curso'),
        ('finished', 'Finalizado'),
        ('cancelled', 'Cancelado'),
    ]

    # Información básica
    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Descripción")
    short_description = models.CharField(
        max_length=300, 
        blank=True,
        verbose_name="Descripción Corta"
    )
    
    # Relaciones
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='events',
        verbose_name="Categoría"
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name="Lugar"
    )
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name="Organizador"
    )
    
    # Fechas
    start_date = models.DateTimeField(verbose_name="Fecha de Inicio")
    end_date = models.DateTimeField(verbose_name="Fecha de Fin")
    registration_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Inicio de Registro"
    )
    registration_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de Registro"
    )
    
    # Configuración
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Estado"
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Capacidad"
    )
    is_free = models.BooleanField(default=False, verbose_name="¿Es Gratuito?")
    is_online = models.BooleanField(default=False, verbose_name="¿Es Virtual?")
    online_url = models.URLField(
        blank=True,
        verbose_name="URL del Evento Virtual"
    )
    
    # Multimedia
    banner_image = models.ImageField(
        upload_to='events/banners/',
        blank=True,
        null=True,
        verbose_name="Banner"
    )
    thumbnail = models.ImageField(
        upload_to='events/thumbnails/',
        blank=True,
        null=True,
        verbose_name="Miniatura"
    )
    
    # Información adicional
    terms_and_conditions = models.TextField(
        blank=True,
        verbose_name="Términos y Condiciones"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Etiquetas",
        help_text="Separadas por comas"
    )
    
    # Contacto
    contact_email = models.EmailField(
        blank=True,
        verbose_name="Email de Contacto"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto"
    )
    
    # Metadata
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Vistas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save para generar slug automáticamente."""
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
            
            # Asegurar que el slug es único
            original_slug = self.slug
            counter = 1
            while Event.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Verifica si el evento está activo."""
        return self.status == 'published' and self.start_date > timezone.now()

    @property
    def is_past(self):
        """Verifica si el evento ya pasó."""
        return self.end_date < timezone.now()

    @property
    def tickets_sold(self):
        """Retorna el número de tickets vendidos."""
        return self.ticket_types.aggregate(
            total=models.Sum('sold_count')
        )['total'] or 0

    @property
    def tickets_available(self):
        """Retorna el número de tickets disponibles."""
        return self.capacity - self.tickets_sold

    @property
    def is_sold_out(self):
        """Verifica si el evento está agotado."""
        return self.tickets_sold >= self.capacity

    def get_tag_list(self):
        """Retorna lista de tags."""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]