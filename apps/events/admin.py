"""
Configuración del admin para eventos.
"""
from django.contrib import admin
from .models import Category, Venue, Event


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'events_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'capacity', 'created_at']
    list_filter = ['city', 'state', 'country']
    search_fields = ['name', 'city', 'address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'venue', 'status', 'start_date', 'organizer', 'tickets_sold']
    list_filter = ['status', 'category', 'is_free', 'is_online', 'start_date']
    search_fields = ['title', 'description', 'organizer__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'tickets_sold', 'tickets_available']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'slug', 'description', 'short_description', 'category')
        }),
        ('Ubicación', {
            'fields': ('venue', 'is_online', 'online_url')
        }),
        ('Fechas', {
            'fields': ('start_date', 'end_date', 'registration_start', 'registration_end')
        }),
        ('Configuración', {
            'fields': ('status', 'capacity', 'is_free', 'organizer')
        }),
        ('Multimedia', {
            'fields': ('banner_image', 'thumbnail')
        }),
        ('Información Adicional', {
            'fields': ('terms_and_conditions', 'tags', 'contact_email', 'contact_phone')
        }),
        ('Estadísticas', {
            'fields': ('views_count', 'created_at', 'updated_at')
        }),
    )