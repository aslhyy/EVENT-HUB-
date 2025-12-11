"""
Filtros para patrocinadores.
"""
from django_filters import rest_framework as filters
from .models import Sponsor, Sponsorship


class SponsorFilter(filters.FilterSet):
    """Filtros para patrocinadores."""
    name = filters.CharFilter(lookup_expr='icontains')
    industry = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=Sponsor.STATUS_CHOICES)
    contact_email = filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Sponsor
        fields = ['name', 'industry', 'status']


class SponsorshipFilter(filters.FilterSet):
    """Filtros para patrocinios."""
    event = filters.NumberFilter(field_name='event__id')
    event_title = filters.CharFilter(field_name='event__title', lookup_expr='icontains')
    sponsor = filters.NumberFilter(field_name='sponsor__id')
    sponsor_name = filters.CharFilter(field_name='sponsor__name', lookup_expr='icontains')
    sponsor_tier = filters.NumberFilter(field_name='sponsor_tier__id')
    status = filters.ChoiceFilter(choices=Sponsorship.STATUS_CHOICES)
    is_active = filters.BooleanFilter()
    amount_min = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    start_date = filters.DateFilter(field_name='start_date')
    start_date_after = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = filters.DateFilter(field_name='start_date', lookup_expr='lte')
    
    class Meta:
        model = Sponsorship
        fields = [
            'event', 'sponsor', 'sponsor_tier', 'status',
            'is_active', 'amount_min', 'amount_max'
        ]