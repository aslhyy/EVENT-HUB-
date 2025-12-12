"""
Serializers para asistentes.
"""
from rest_framework import serializers
from django.utils import timezone
from .models import Attendee, CheckInLog, Survey, SurveyQuestion, SurveyResponse
from apps.tickets.serializers import TicketSerializer
from apps.events.serializers import EventListSerializer


class AttendeeSerializer(serializers.ModelSerializer):
    """Serializer básico para asistentes."""
    event_title = serializers.CharField(source='event.title', read_only=True)
    ticket_code = serializers.CharField(source='ticket.code', read_only=True)
    is_checked_in = serializers.BooleanField(read_only=True)
    can_check_in = serializers.BooleanField(read_only=True)
    total_check_ins = serializers.IntegerField(read_only=True)

    class Meta:
        model = Attendee
        fields = [
            'id', 'user', 'ticket', 'ticket_code', 'event', 'event_title',
            'full_name', 'email', 'phone', 'document_type', 'document_number',
            'status', 'checked_in_at', 'special_requirements',
            'dietary_restrictions', 'emergency_contact_name',
            'emergency_contact_phone', 'is_checked_in', 'can_check_in',
            'total_check_ins', 'created_at'
        ]
        read_only_fields = ['user', 'checked_in_at', 'checked_in_by']


class AttendeeDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para asistentes."""
    ticket = TicketSerializer(read_only=True)
    event = EventListSerializer(read_only=True)
    is_checked_in = serializers.BooleanField(read_only=True)
    can_check_in = serializers.BooleanField(read_only=True)
    total_check_ins = serializers.IntegerField(read_only=True)
    check_in_history = serializers.SerializerMethodField()

    class Meta:
        model = Attendee
        fields = [
            'id', 'user', 'ticket', 'event', 'full_name', 'email', 'phone',
            'document_type', 'document_number', 'status', 'checked_in_at',
            'checked_in_by', 'special_requirements', 'dietary_restrictions',
            'emergency_contact_name', 'emergency_contact_phone', 'notes',
            'is_checked_in', 'can_check_in', 'total_check_ins',
            'check_in_history', 'created_at', 'updated_at'
        ]

    def get_check_in_history(self, obj):
        logs = obj.check_in_logs.all()[:5]  # Últimos 5 check-ins
        return CheckInLogSerializer(logs, many=True).data


class CheckInSerializer(serializers.Serializer):
    """Serializer para realizar check-in."""
    ticket_code = serializers.CharField(max_length=50, required=False)
    ticket_uuid = serializers.UUIDField(required=False)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if not data.get('ticket_code') and not data.get('ticket_uuid'):
            raise serializers.ValidationError(
                "Debe proporcionar ticket_code o ticket_uuid"
            )
        return data


class CheckInLogSerializer(serializers.ModelSerializer):
    """Serializer para registros de check-in."""
    attendee_name = serializers.CharField(source='attendee.full_name', read_only=True)
    event_title = serializers.CharField(source='attendee.event.title', read_only=True)
    checked_in_by_name = serializers.SerializerMethodField()

    class Meta:
        model = CheckInLog
        fields = [
            'id', 'attendee', 'attendee_name', 'event_title',
            'checked_in_at', 'checked_in_by', 'checked_in_by_name',
            'location', 'device_info', 'ip_address', 'notes'
        ]

    def get_checked_in_by_name(self, obj):
        if obj.checked_in_by:
            return obj.checked_in_by.get_full_name() or obj.checked_in_by.username
        return None


class SurveyQuestionSerializer(serializers.ModelSerializer):
    """Serializer para preguntas de encuesta."""
    
    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'survey', 'question_text', 'question_type',
            'options', 'is_required', 'order', 'created_at'
        ]


class SurveySerializer(serializers.ModelSerializer):
    """Serializer básico para encuestas."""
    event_title = serializers.CharField(source='event.title', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    total_responses = serializers.IntegerField(read_only=True)
    response_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'event', 'event_title', 'title', 'description',
            'status', 'start_date', 'end_date', 'is_anonymous',
            'allow_multiple_responses', 'is_active', 'total_responses',
            'response_rate', 'created_at'
        ]
        read_only_fields = ['created_by']


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para encuestas con preguntas."""
    event = EventListSerializer(read_only=True)
    questions = SurveyQuestionSerializer(many=True, read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    total_responses = serializers.IntegerField(read_only=True)
    response_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'event', 'title', 'description', 'status',
            'start_date', 'end_date', 'is_anonymous',
            'allow_multiple_responses', 'questions', 'is_active',
            'total_responses', 'response_rate', 'created_by',
            'created_at', 'updated_at'
        ]


class SurveyResponseSerializer(serializers.ModelSerializer):
    """Serializer para respuestas de encuesta."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    respondent_name = serializers.SerializerMethodField()

    class Meta:
        model = SurveyResponse
        fields = [
            'id', 'question', 'question_text', 'respondent',
            'respondent_name', 'attendee', 'text_response',
            'rating_response', 'choice_response', 'responded_at'
        ]
        read_only_fields = ['respondent', 'responded_at']

    def get_respondent_name(self, obj):
        if obj.question.survey.is_anonymous:
            return "Anónimo"
        if obj.respondent:
            return obj.respondent.get_full_name() or obj.respondent.username
        return "Anónimo"


class SubmitSurveySerializer(serializers.Serializer):
    """Serializer para enviar respuestas de encuesta."""
    survey = serializers.PrimaryKeyRelatedField(queryset=Survey.objects.all())
    responses = serializers.ListField(
        child=serializers.DictField()
    )

    def validate_responses(self, value):
        """Validar formato de respuestas."""
        for response in value:
            if 'question_id' not in response:
                raise serializers.ValidationError(
                    "Cada respuesta debe tener question_id"
                )
        return value

    def validate(self, data):
        """Validar que la encuesta esté activa."""
        survey = data['survey']
        
        if not survey.is_active:
            raise serializers.ValidationError("La encuesta no está activa")
        
        # Validar respuestas obligatorias
        required_questions = survey.questions.filter(is_required=True)
        provided_question_ids = [r['question_id'] for r in data['responses']]
        
        for question in required_questions:
            if question.id not in provided_question_ids:
                raise serializers.ValidationError(
                    f"La pregunta '{question.question_text}' es obligatoria"
                )
        
        return data


class AttendeeExportSerializer(serializers.ModelSerializer):
    """Serializer para exportación de asistentes."""
    event_title = serializers.CharField(source='event.title')
    ticket_code = serializers.CharField(source='ticket.code')
    ticket_type = serializers.CharField(source='ticket.ticket_type.name')
    check_in_count = serializers.SerializerMethodField()

    class Meta:
        model = Attendee
        fields = [
            'id', 'event_title', 'full_name', 'email', 'phone',
            'document_type', 'document_number', 'ticket_code',
            'ticket_type', 'status', 'checked_in_at', 'check_in_count',
            'special_requirements', 'dietary_restrictions',
            'emergency_contact_name', 'emergency_contact_phone'
        ]

    def get_check_in_count(self, obj):
        return obj.check_in_logs.count()