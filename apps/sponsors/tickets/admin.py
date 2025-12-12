"""
Configuración del admin para tickets.
"""
from django.contrib import admin
from .models import TicketType, Ticket, DiscountCode


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'event', 'price', 'quantity', 
        'sold_count', 'available_quantity', 'is_active'
    ]
    list_filter = ['is_active', 'event__category', 'sale_start']
    search_fields = ['name', 'event__title']
    readonly_fields = ['sold_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('event', 'name', 'description', 'color')
        }),
        ('Precio y Cantidad', {
            'fields': ('price', 'quantity', 'sold_count')
        }),
        ('Límites de Compra', {
            'fields': ('min_purchase', 'max_purchase')
        }),
        ('Fechas de Venta', {
            'fields': ('sale_start', 'sale_end')
        }),
        ('Configuración', {
            'fields': ('is_active', 'benefits')
        }),
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'ticket_type', 'buyer', 'attendee_name',
        'status', 'purchase_price', 'purchased_at'
    ]
    list_filter = ['status', 'ticket_type__event', 'purchased_at']
    search_fields = ['code', 'attendee_name', 'attendee_email', 'buyer__username']
    readonly_fields = [
        'code', 'uuid', 'qr_code', 'pdf_ticket', 
        'purchased_at', 'used_at', 'cancelled_at'
    ]
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('ticket_type', 'code', 'uuid', 'status')
        }),
        ('Comprador', {
            'fields': ('buyer',)
        }),
        ('Asistente', {
            'fields': ('attendee_name', 'attendee_email', 'attendee_phone')
        }),
        ('Pago', {
            'fields': ('purchase_price', 'discount_applied', 'discount_code')
        }),
        ('Archivos', {
            'fields': ('qr_code', 'pdf_ticket')
        }),
        ('Fechas', {
            'fields': ('purchased_at', 'used_at', 'cancelled_at')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )


@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'event', 'discount_type', 'discount_value',
        'used_count', 'max_uses', 'is_active', 'valid_until'
    ]
    list_filter = ['discount_type', 'is_active', 'event']
    search_fields = ['code', 'event__title']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_ticket_types']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('event', 'code', 'description')
        }),
        ('Descuento', {
            'fields': ('discount_type', 'discount_value', 'minimum_purchase')
        }),
        ('Límites', {
            'fields': ('max_uses', 'used_count', 'max_uses_per_user')
        }),
        ('Vigencia', {
            'fields': ('valid_from', 'valid_until', 'is_active')
        }),
        ('Tipos Aplicables', {
            'fields': ('applicable_ticket_types',)
        }),
    )