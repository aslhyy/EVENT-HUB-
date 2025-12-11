"""
Serializers para eventos.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Venue, Event


class CategorySerializer(serializers.ModelSerializer):
    """Serializer básico para categorías."""
    events_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'events_count', 'created_at']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para categorías con eventos."""
    events_count = serializers.IntegerField(read_only=True)
    recent_events = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'icon', 
            'events_count', 'recent_events', 'created_at', 'updated_at'
        ]

    def get_recent_events(self, obj):
        """Obtiene los 5 eventos más recientes de la categoría."""
        events = obj.events.filter(status='published').order_by('-start_date')[:5]
        return EventListSerializer(events, many=True).data


class VenueSerializer(serializers.ModelSerializer):
    """Serializer básico para lugares."""
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'address', 'city', 'state', 'country',
            'postal_code', 'capacity', 'latitude', 'longitude',
            'full_address', 'description', 'amenities', 'image'
        ]


class VenueDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para lugares con eventos."""
    full_address = serializers.CharField(read_only=True)
    upcoming_events_count = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            'id', 'name', 'address', 'city', 'state', 'country',
            'postal_code', 'capacity', 'latitude', 'longitude',
            'full_address', 'description', 'amenities', 'image',
            'upcoming_events_count', 'created_at', 'updated_at'
        ]

    def get_upcoming_events_count(self, obj):
        """Cuenta eventos próximos en este lugar."""
        from django.utils import timezone
        return obj.events.filter(
            status='published',
            start_date__gte=timezone.now()
        ).count()


class OrganizerSerializer(serializers.ModelSerializer):
    """Serializer para organizadores."""
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class EventListSerializer(serializers.ModelSerializer):
    """Serializer para listado de eventos."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    venue_name = serializers.CharField(source='venue.name', read_only=True)
    organizer_name = serializers.SerializerMethodField()
    tickets_available = serializers.IntegerField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'short_description', 'category_name',
            'venue_name', 'organizer_name', 'start_date', 'end_date',
            'status', 'capacity', 'tickets_available', 'is_free',
            'is_online', 'is_sold_out', 'thumbnail', 'views_count'
        ]

    def get_organizer_name(self, obj):
        return obj.organizer.get_full_name() or obj.organizer.username


class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para eventos."""
    category = CategorySerializer(read_only=True)
    venue = VenueSerializer(read_only=True)
    organizer = OrganizerSerializer(read_only=True)
    tickets_sold = serializers.IntegerField(read_only=True)
    tickets_available = serializers.IntegerField(read_only=True)
    is_sold_out = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    tag_list = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'venue', 'organizer', 'start_date', 'end_date',
            'registration_start', 'registration_end', 'status', 'capacity',
            'tickets_sold', 'tickets_available', 'is_free', 'is_online',
            'online_url', 'banner_image', 'thumbnail', 'terms_and_conditions',
            'tags', 'tag_list', 'contact_email', 'contact_phone',
            'views_count', 'is_sold_out', 'is_active', 'is_past',
            'created_at', 'updated_at'
        ]

    def get_tag_list(self, obj):
        return obj.get_tag_list()


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar eventos."""
    
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 'category',
            'venue', 'start_date', 'end_date', 'registration_start',
            'registration_end', 'status', 'capacity', 'is_free',
            'is_online', 'online_url', 'banner_image', 'thumbnail',
            'terms_and_conditions', 'tags', 'contact_email', 'contact_phone'
        ]

    def validate(self, data):
        """Validaciones personalizadas."""
        # Validar fechas
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    "La fecha de fin debe ser posterior a la fecha de inicio."
                )

        # Validar registro
        if data.get('registration_start') and data.get('registration_end'):
            if data['registration_end'] <= data['registration_start']:
                raise serializers.ValidationError(
                    "La fecha de fin de registro debe ser posterior al inicio."
                )

        # Validar URL si es online
        if data.get('is_online') and not data.get('online_url'):
            raise serializers.ValidationError(
                "Debe proporcionar una URL para eventos virtuales."
            )

        return data

    def create(self, validated_data):
        """Asignar organizador automáticamente."""
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class EventStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas del evento."""
    total_capacity = serializers.IntegerField()
    tickets_sold = serializers.IntegerField()
    tickets_available = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    attendees_checked_in = serializers.IntegerField()
    conversion_rate = serializers.FloatField()