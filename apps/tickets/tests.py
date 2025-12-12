"""
Tests para tickets.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from apps.events.models import Event, Category, Venue
from .models import TicketType, Ticket, DiscountCode


class TicketTypeModelTest(TestCase):
    """Tests para el modelo TicketType."""
    
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
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name="General",
            price=Decimal('50000.00'),
            quantity=100,
            is_active=True
        )
    
    def test_ticket_type_creation(self):
        """Test de creación de tipo de ticket."""
        self.assertEqual(self.ticket_type.name, "General")
        self.assertEqual(self.ticket_type.price, Decimal('50000.00'))
        self.assertEqual(self.ticket_type.quantity, 100)
    
    def test_available_quantity(self):
        """Test de cantidad disponible."""
        self.assertEqual(self.ticket_type.available_quantity, 100)
        
        self.ticket_type.sold_count = 30
        self.ticket_type.save()
        self.assertEqual(self.ticket_type.available_quantity, 70)
    
    def test_is_available(self):
        """Test de disponibilidad."""
        self.assertTrue(self.ticket_type.is_available)
        
        self.ticket_type.sold_count = 100
        self.ticket_type.save()
        self.assertFalse(self.ticket_type.is_available)
    
    def test_percentage_sold(self):
        """Test de porcentaje vendido."""
        self.ticket_type.sold_count = 50
        self.ticket_type.save()
        self.assertEqual(self.ticket_type.percentage_sold, 50.0)


class TicketModelTest(TestCase):
    """Tests para el modelo Ticket."""
    
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
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name="General",
            price=Decimal('50000.00'),
            quantity=100
        )
    
    def test_ticket_creation(self):
        """Test de creación de ticket."""
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            buyer=self.user,
            attendee_name="Juan Pérez",
            attendee_email="juan@example.com",
            purchase_price=Decimal('50000.00')
        )
        
        self.assertIsNotNone(ticket.code)
        self.assertEqual(ticket.status, 'active')
        self.assertTrue(ticket.is_valid)
    
    def test_code_generation(self):
        """Test de generación automática de código."""
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            buyer=self.user,
            attendee_name="Juan Pérez",
            attendee_email="juan@example.com",
            purchase_price=Decimal('50000.00')
        )
        
        self.assertIsNotNone(ticket.code)
        self.assertEqual(len(ticket.code), 12)
    
    def test_final_price(self):
        """Test de precio final con descuento."""
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            buyer=self.user,
            attendee_name="Juan Pérez",
            attendee_email="juan@example.com",
            purchase_price=Decimal('50000.00'),
            discount_applied=Decimal('5000.00')
        )
        
        self.assertEqual(ticket.final_price, Decimal('45000.00'))


class TicketAPITest(APITestCase):
    """Tests para la API de tickets."""
    
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
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name="General",
            price=Decimal('50000.00'),
            quantity=100,
            is_active=True
        )
    
    def test_purchase_ticket_unauthorized(self):
        """Test de compra sin autenticación."""
        data = {
            'ticket_type': self.ticket_type.id,
            'quantity': 1,
            'attendee_name': 'Juan Pérez',
            'attendee_email': 'juan@example.com'
        }
        response = self.client.post('/api/tickets/purchase/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_purchase_ticket_authorized(self):
        """Test de compra con autenticación."""
        self.client.force_authenticate(user=self.user)
        data = {
            'ticket_type': self.ticket_type.id,
            'quantity': 2,
            'attendee_name': 'Juan Pérez',
            'attendee_email': 'juan@example.com'
        }
        response = self.client.post('/api/tickets/purchase/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['tickets']), 2)