"""
Tests para eventos.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Category, Venue, Event


class CategoryModelTest(TestCase):
    """Tests para el modelo Category."""
    
    def setUp(self):
        self.category = Category.objects.create(
            name="Conciertos",
            description="Eventos musicales"
        )
    
    def test_category_creation(self):
        """Test de creación de categoría."""
        self.assertEqual(self.category.name, "Conciertos")
        self.assertTrue(isinstance(self.category, Category))
        self.assertEqual(str(self.category), "Conciertos")
    
    def test_events_count(self):
        """Test de contador de eventos."""
        self.assertEqual(self.category.events_count, 0)


class VenueModelTest(TestCase):
    """Tests para el modelo Venue."""
    
    def setUp(self):
        self.venue = Venue.objects.create(
            name="Teatro Colón",
            address="Calle 10 # 5-32",
            city="Bogotá",
            state="Cundinamarca",
            capacity=1500
        )
    
    def test_venue_creation(self):
        """Test de creación de lugar."""
        self.assertEqual(self.venue.name, "Teatro Colón")
        self.assertEqual(self.venue.capacity, 1500)
        self.assertTrue("Bogotá" in str(self.venue))
    
    def test_full_address(self):
        """Test de dirección completa."""
        expected_address = "Calle 10 # 5-32, Bogotá, Cundinamarca, Colombia"
        self.assertEqual(self.venue.full_address, expected_address)


class EventModelTest(TestCase):
    """Tests para el modelo Event."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Conciertos")
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            state="Test State",
            capacity=1000
        )
        
        self.event = Event.objects.create(
            title="Concierto de Rock",
            description="Gran concierto de rock",
            category=self.category,
            venue=self.venue,
            organizer=self.user,
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=30, hours=3),
            capacity=500,
            status='published'
        )
    
    def test_event_creation(self):
        """Test de creación de evento."""
        self.assertEqual(self.event.title, "Concierto de Rock")
        self.assertEqual(self.event.capacity, 500)
        self.assertTrue(isinstance(self.event, Event))
    
    def test_slug_generation(self):
        """Test de generación automática de slug."""
        self.assertIsNotNone(self.event.slug)
        self.assertTrue("concierto" in self.event.slug.lower())
    
    def test_is_active(self):
        """Test de verificación si evento está activo."""
        self.assertTrue(self.event.is_active)
    
    def test_tickets_available(self):
        """Test de tickets disponibles."""
        self.assertEqual(self.event.tickets_available, 500)


class EventAPITest(APITestCase):
    """Tests para la API de eventos."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Conciertos")
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            state="Test State",
            capacity=1000
        )
    
    def test_list_events(self):
        """Test de listar eventos."""
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_event_unauthorized(self):
        """Test de crear evento sin autenticación."""
        data = {
            'title': 'Nuevo Evento',
            'description': 'Descripción',
            'category': self.category.id,
            'start_date': timezone.now() + timedelta(days=30),
            'end_date': timezone.now() + timedelta(days=30, hours=3),
            'capacity': 100
        }
        response = self.client.post('/api/events/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_event_authorized(self):
        """Test de crear evento con autenticación."""
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'Nuevo Evento',
            'description': 'Descripción del evento',
            'category': self.category.id,
            'venue': self.venue.id,
            'start_date': (timezone.now() + timedelta(days=30)).isoformat(),
            'end_date': (timezone.now() + timedelta(days=30, hours=3)).isoformat(),
            'capacity': 100,
            'status': 'draft'
        }
        response = self.client.post('/api/events/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)