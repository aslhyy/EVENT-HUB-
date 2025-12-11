"""
Filtros para eventos.
"""
from django_filters import rest_framework as filters
from .models import Event


class EventFilter(filters.FilterSet):
    """
    Filtros avanzados para eventos.
    """
    title = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    category = filters.NumberFilter(field_name='category__id')
    category_name = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    venue = filters.NumberFilter(field_name='venue__id')
    city = filters.CharFilter(field_name='venue__city', lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Event.STATUS_CHOICES)
    is_free = filters.BooleanFilter()
    is_online = filters.BooleanFilter()
    
    # Filtros de fecha
    start_date = filters.DateFilter(field_name='start_date', lookup_expr='date')
    start_date_gte = filters.DateTimeFilter(field_name='start_date', lookup_expr='gte')
    start_date_lte = filters.DateTimeFilter(field_name='start_date', lookup_expr='lte')
    end_date = filters.DateFilter(field_name='end_date', lookup_expr='date')
    end_date_gte = filters.DateTimeFilter(field_name='end_date', lookup_expr='gte')
    end_date_lte = filters.DateTimeFilter(field_name='end_date', lookup_expr='lte')
    
    # Filtros de capacidad
    capacity_gte = filters.NumberFilter(field_name='capacity', lookup_expr='gte')
    capacity_lte = filters.NumberFilter(field_name='capacity', lookup_expr='lte')
    
    # Filtros por organizador
    organizer = filters.NumberFilter(field_name='organizer__id')
    organizer_username = filters.CharFilter(field_name='organizer__username', lookup_expr='icontains')

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'category', 'category_name', 'venue',
            'city', 'status', 'is_free', 'is_online', 'start_date',
            'start_date_gte', 'start_date_lte', 'end_date', 'end_date_gte',
            'end_date_lte', 'capacity_gte', 'capacity_lte', 'organizer',
            'organizer_username'
        ]