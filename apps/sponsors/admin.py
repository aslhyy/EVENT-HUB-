"""
Configuración del admin para patrocinadores.
"""
from django.contrib import admin
from .models import SponsorTier, Sponsor, Sponsorship, SponsorBenefit


@admin.register(SponsorTier)
class SponsorTierAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'min_amount', 'max_amount', 'order',
        'sponsors_count', 'is_active'
    ]
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'sponsors_count']


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'industry', 'status', 'contact_email',
        'total_sponsorships', 'total_invested'
    ]
    list_filter = ['status', 'industry', 'created_at']
    search_fields = ['name', 'contact_name', 'contact_email', 'industry']
    readonly_fields = ['created_at', 'updated_at', 'total_sponsorships', 'total_invested']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'logo', 'description', 'industry', 'status')
        }),
        ('Contacto', {
            'fields': (
                'contact_name', 'contact_email', 'contact_phone',
                'contact_position'
            )
        }),
        ('Redes Sociales', {
            'fields': ('website', 'facebook', 'twitter', 'instagram', 'linkedin')
        }),
        ('Información Fiscal', {
            'fields': ('tax_id', 'billing_address')
        }),
        ('Metadata', {
            'fields': ('notes', 'tags', 'created_at', 'updated_at')
        }),
        ('Estadísticas', {
            'fields': ('total_sponsorships', 'total_invested')
        }),
    )


@admin.register(Sponsorship)
class SponsorshipAdmin(admin.ModelAdmin):
    list_display = [
        'sponsor', 'event', 'sponsor_tier', 'amount',
        'status', 'is_active', 'start_date', 'end_date'
    ]
    list_filter = ['status', 'is_active', 'sponsor_tier', 'start_date']
    search_fields = ['sponsor__name', 'event__title']
    readonly_fields = ['created_at', 'updated_at', 'is_current', 'days_remaining']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('event', 'sponsor', 'sponsor_tier', 'status', 'is_active')
        }),
        ('Financiero', {
            'fields': ('amount', 'currency')
        }),
        ('Fechas', {
            'fields': (
                'start_date', 'end_date', 'contract_signed_date',
                'is_current', 'days_remaining'
            )
        }),
        ('Documentos', {
            'fields': ('contract_document',)
        }),
        ('Visibilidad', {
            'fields': ('logo_placement', 'booth_number')
        }),
        ('Métricas', {
            'fields': ('impressions', 'clicks', 'leads_generated')
        }),
        ('Notas', {
            'fields': ('notes', 'internal_notes')
        }),
    )


@admin.register(SponsorBenefit)
class SponsorBenefitAdmin(admin.ModelAdmin):
    list_display = [
        'sponsorship', 'benefit_type', 'quantity',
        'delivered', 'delivered_date'
    ]
    list_filter = ['benefit_type', 'delivered', 'delivered_date']
    search_fields = ['sponsorship__sponsor__name', 'description']
    readonly_fields = ['created_at', 'updated_at']