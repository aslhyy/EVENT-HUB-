"""
Filtros para asistentes.
"""
from django_filters import rest_framework as filters
from .models import Attendee


class AttendeeFilter(filters.FilterSet):
    """Filtros para asistentes."""
    event = filters.NumberFilter(field_name='event__id')
    event_title = filters.CharFilter(field_name='event__title', lookup_expr='icontains')
    full_name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Attendee.STATUS_CHOICES)
    checked_in = filters.BooleanFilter(method='filter_checked_in')
    document_number = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Attendee
        fields = ['event', 'event_title', 'status', 'full_name', 'email']
    
    def filter_checked_in(self, queryset, name, value):
        """Filtrar por check-in realizado."""
        if value:
            return queryset.filter(status='checked_in')
        return queryset.exclude(status='checked_in')