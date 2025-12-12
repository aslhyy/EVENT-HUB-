"""
Filtros para tickets.
"""
from django_filters import rest_framework as filters
from .models import TicketType, Ticket


class TicketTypeFilter(filters.FilterSet):
    """Filtros para tipos de tickets."""
    event = filters.NumberFilter(field_name='event__id')
    event_title = filters.CharFilter(field_name='event__title', lookup_expr='icontains')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte')
    available = filters.BooleanFilter(method='filter_available')
    
    class Meta:
        model = TicketType
        fields = ['event', 'event_title', 'is_active', 'price_min', 'price_max']
    
    def filter_available(self, queryset, name, value):
        """Filtrar solo tickets disponibles."""
        if value:
            from django.db.models import F
            return queryset.filter(
                is_active=True,
                sold_count__lt=F('quantity')
            )
        return queryset


class TicketFilter(filters.FilterSet):
    """Filtros para tickets."""
    event = filters.NumberFilter(field_name='ticket_type__event__id')
    event_title = filters.CharFilter(field_name='ticket_type__event__title', lookup_expr='icontains')
    ticket_type = filters.NumberFilter(field_name='ticket_type__id')
    buyer = filters.NumberFilter(field_name='buyer__id')
    status = filters.ChoiceFilter(choices=Ticket.STATUS_CHOICES)
    code = filters.CharFilter(lookup_expr='iexact')
    purchased_date = filters.DateFilter(field_name='purchased_at', lookup_expr='date')
    purchased_after = filters.DateTimeFilter(field_name='purchased_at', lookup_expr='gte')
    purchased_before = filters.DateTimeFilter(field_name='purchased_at', lookup_expr='lte')
    
    class Meta:
        model = Ticket
        fields = ['event', 'event_title', 'ticket_type', 'buyer', 'status', 'code']