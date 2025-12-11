"""
Configuración del admin para asistentes.
"""
from django.contrib import admin
from .models import Attendee, CheckInLog, Survey, SurveyQuestion, SurveyResponse


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'event', 'status',
        'checked_in_at', 'total_check_ins'
    ]
    list_filter = ['status', 'event', 'checked_in_at']
    search_fields = ['full_name', 'email', 'document_number', 'ticket__code']
    readonly_fields = ['created_at', 'updated_at', 'total_check_ins']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'ticket', 'event', 'status')
        }),
        ('Datos Personales', {
            'fields': (
                'full_name', 'email', 'phone',
                'document_type', 'document_number'
            )
        }),
        ('Check-in', {
            'fields': ('checked_in_at', 'checked_in_by', 'total_check_ins')
        }),
        ('Información Adicional', {
            'fields': (
                'special_requirements', 'dietary_restrictions',
                'emergency_contact_name', 'emergency_contact_phone'
            )
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )


@admin.register(CheckInLog)
class CheckInLogAdmin(admin.ModelAdmin):
    list_display = [
        'attendee', 'checked_in_at', 'checked_in_by', 'location'
    ]
    list_filter = ['checked_in_at', 'attendee__event']
    search_fields = ['attendee__full_name', 'location']
    readonly_fields = ['checked_in_at']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event', 'status', 'total_responses',
        'response_rate', 'is_active'
    ]
    list_filter = ['status', 'is_anonymous', 'event']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'total_responses', 'response_rate']


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'survey', 'question_type', 'is_required', 'order']
    list_filter = ['question_type', 'is_required', 'survey']
    search_fields = ['question_text']
    ordering = ['survey', 'order']


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = [
        'question', 'respondent', 'responded_at'
    ]
    list_filter = ['question__survey', 'responded_at']
    search_fields = ['respondent__username', 'text_response']
    readonly_fields = ['responded_at']