"""
Tests para asistentes.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status

from apps.events.models import Event, Category, Venue
from apps.tickets.models import TicketType, Ticket
from .models import Attendee, CheckInLog, Survey


class AttendeeModelTest(TestCase):
    """Tests para el modelo Attendee."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.category = Category.objects.create(name="Conciertos")
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            state="Test State",
            capacity=1000
        )
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            category=self.category,
            venue=self.venue,
            organizer=self.user,
            start_date=timezone.now() + timedelta(hours=1),
            end_date=timezone.now() + timedelta(hours=4),
            capacity=500,
            status='published'
        )
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name="General",
            price=50000,
            quantity=100
        )
        self.ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            buyer=self.user,
            attendee_name="Juan Pérez",
            attendee_email="juan@example.com",
            purchase_price=50000
        )
        self.attendee = Attendee.objects.create(
            user=self.user,
            ticket=self.ticket,
            event=self.event,
            full_name="Juan Pérez",
            email="juan@example.com"
        )
    
    def test_attendee_creation(self):
        """Test de creación de asistente."""
        self.assertEqual(self.attendee.full_name, "Juan Pérez")
        self.assertEqual(self.attendee.status, 'registered')
    
    def test_can_check_in(self):
        """Test de verificación de check-in."""
        self.assertTrue(self.attendee.can_check_in)
    
    def test_is_checked_in(self):
        """Test de verificación de estado check-in."""
        self.assertFalse(self.attendee.is_checked_in)
        
        self.attendee.status = 'checked_in'
        self.attendee.save()
        self.assertTrue(self.attendee.is_checked_in)


class SurveyModelTest(TestCase):
    """Tests para el modelo Survey."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.category = Category.objects.create(name="Conciertos")
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            state="Test State",
            capacity=1000
        )
        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            category=self.category,
            venue=self.venue,
            organizer=self.user,
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=30, hours=3),
            capacity=500,
            status='published'
        )
        self.survey = Survey.objects.create(
            event=self.event,
            title="Encuesta de Satisfacción",
            status='active',
            created_by=self.user,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7)
        )
    
    def test_survey_creation(self):
        """Test de creación de encuesta."""
        self.assertEqual(self.survey.title, "Encuesta de Satisfacción")
        self.assertEqual(self.survey.status, 'active')
    
    def test_is_active(self):
        """Test de verificación de encuesta activa."""
        self.assertTrue(self.survey.is_active)