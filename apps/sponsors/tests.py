"""
Tests para patrocinadores.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from apps.events.models import Event, Category, Venue
from .models import SponsorTier, Sponsor, Sponsorship, SponsorBenefit


class SponsorTierModelTest(TestCase):
    """Tests para el modelo SponsorTier."""
    
    def setUp(self):
        self.tier = SponsorTier.objects.create(
            name="Gold",
            min_amount=Decimal('5000000.00'),
            max_amount=Decimal('10000000.00'),
            order=2
        )
    
    def test_tier_creation(self):
        """Test de creación de nivel."""
        self.assertEqual(self.tier.name, "Gold")
        self.assertEqual(self.tier.min_amount, Decimal('5000000.00'))


class SponsorModelTest(TestCase):
    """Tests para el modelo Sponsor."""
    
    def setUp(self):
        self.sponsor = Sponsor.objects.create(
            name="Tech Corp",
            industry="Tecnología",
            contact_email="contact@techcorp.com",
            status='active'
        )
    
    def test_sponsor_creation(self):
        """Test de creación de patrocinador."""
        self.assertEqual(self.sponsor.name, "Tech Corp")
        self.assertEqual(self.sponsor.status, 'active')
    
    def test_total_sponsorships(self):
        """Test de contador de patrocinios."""
        self.assertEqual(self.sponsor.total_sponsorships, 0)


class SponsorshipModelTest(TestCase):
    """Tests para el modelo Sponsorship."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.category = Category.objects.create(name="Conferencias")
        self.venue = Venue.objects.create(
            name="Test Venue",
            address="Test Address",
            city="Test City",
            state="Test State",
            capacity=1000
        )
        self.event = Event.objects.create(
            title="Tech Conference 2025",
            description="Test Description",
            category=self.category,
            venue=self.venue,
            organizer=self.user,
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=32),
            capacity=500,
            status='published'
        )
        self.tier = SponsorTier.objects.create(
            name="Gold",
            min_amount=Decimal('5000000.00')
        )
        self.sponsor = Sponsor.objects.create(
            name="Tech Corp",
            contact_email="contact@techcorp.com"
        )
        self.sponsorship = Sponsorship.objects.create(
            event=self.event,
            sponsor=self.sponsor,
            sponsor_tier=self.tier,
            amount=Decimal('8000000.00'),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            status='active'
        )
    
    def test_sponsorship_creation(self):
        """Test de creación de patrocinio."""
        self.assertEqual(self.sponsorship.amount, Decimal('8000000.00'))
        self.assertEqual(self.sponsorship.status, 'active')
    
    def test_is_current(self):
        """Test de verificación de patrocinio vigente."""
        self.assertTrue(self.sponsorship.is_current)
    
    def test_roi_metrics(self):
        """Test de métricas ROI."""
        self.sponsorship.impressions = 10000
        self.sponsorship.clicks = 500
        self.sponsorship.leads_generated = 50
        self.sponsorship.save()
        
        metrics = self.sponsorship.roi_metrics
        self.assertEqual(metrics['impressions'], 10000)
        self.assertEqual(metrics['clicks'], 500)
        self.assertEqual(metrics['ctr'], 5.0)


class SponsorAPITest(APITestCase):
    """Tests para la API de patrocinadores."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.sponsor = Sponsor.objects.create(
            name="Tech Corp",
            contact_email="contact@techcorp.com"
        )
    
    def test_list_sponsors(self):
        """Test de listar patrocinadores."""
        response = self.client.get('/api/sponsors/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_sponsor(self):
        """Test de crear patrocinador."""
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Sponsor',
            'contact_email': 'new@sponsor.com',
            'industry': 'Tech',
            'status': 'active'
        }
        response = self.client.post('/api/sponsors/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)