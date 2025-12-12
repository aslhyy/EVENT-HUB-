from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.events.models import Category, Venue, Event
from apps.tickets.models import TicketType, DiscountCode
from apps.sponsors.models import SponsorTier, Sponsor, Sponsorship
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Inicializa la base de datos con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Inicializando base de datos...'))

        try:
            # Crear usuarios
            self.stdout.write('\n👤 Creando usuarios...')
            organizers = self.create_users()
            
            # Crear categorías
            self.stdout.write('\n📂 Creando categorías...')
            categories = self.create_categories()
            
            # Crear venues
            self.stdout.write('\n📍 Creando lugares...')
            venues = self.create_venues()
            
            # Crear eventos
            self.stdout.write('\n🎪 Creando eventos...')
            events = self.create_events(organizers, categories, venues)
            
            # Crear tipos de tickets
            self.stdout.write('\n🎫 Creando tipos de tickets...')
            self.create_ticket_types(events)
            
            # Crear sponsor tiers
            self.stdout.write('\n💎 Creando niveles de patrocinio...')
            tiers = self.create_sponsor_tiers()
            
            # Crear sponsors
            self.stdout.write('\n🤝 Creando patrocinadores...')
            sponsors = self.create_sponsors()
            
            # Crear patrocinios
            self.stdout.write('\n💼 Creando patrocinios...')
            self.create_sponsorships(sponsors, events, tiers)
            
            # Resumen
            self.print_summary()
            
            self.stdout.write(self.style.SUCCESS('\n✅ ¡Base de datos inicializada exitosamente!\n'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}\n'))
            import traceback
            traceback.print_exc()

    def create_users(self):
        # Admin
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@eventhub.com',
                'is_staff': True,
                'is_superuser': True,
                'first_name': 'Admin',
                'last_name': 'EventHub'
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write('  ✅ Admin creado')
        
        # Organizadores
        organizers = []
        for name in ['Sarah', 'Karen', 'Neyireth', 'Aslhy']:
            user, created = User.objects.get_or_create(
                username=name.lower(),
                defaults={
                    'email': f'{name.lower()}@eventhub.com',
                    'first_name': name,
                    'last_name': 'Organizer',
                    'is_staff': True
                }
            )
            if created:
                user.set_password(f'{name.lower()}123')
                user.save()
                self.stdout.write(f'  ✅ {name} creado')
            organizers.append(user)
        
        # Usuarios normales
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': 'Usuario',
                    'last_name': str(i)
                }
            )
            if created:
                user.set_password('user123')
                user.save()
        
        self.stdout.write(f'  ✅ Total usuarios: {User.objects.count()}')
        return organizers

    def create_categories(self):
        categories_data = [
            ('Conciertos', '🎵', 'Eventos musicales en vivo'),
            ('Conferencias', '🎤', 'Charlas y presentaciones profesionales'),
            ('Deportes', '⚽', 'Eventos deportivos y competencias'),
            ('Teatro', '🎭', 'Obras de teatro y espectáculos'),
            ('Festivales', '🎉', 'Festivales culturales y celebraciones'),
            ('Tecnología', '💻', 'Eventos tech y hackathons'),
            ('Arte', '🎨', 'Exposiciones y eventos artísticos'),
            ('Gastronomía', '🍽️', 'Eventos culinarios y degustaciones'),
        ]
        
        categories = []
        for name, icon, description in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'description': description}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  ✅ {name}')
        
        self.stdout.write(f'  ✅ {len(categories)} categorías creadas')
        return categories

    def create_venues(self):
        venues_data = [
            {
                'name': 'Teatro Colón',
                'address': 'Calle 10 # 5-32',
                'city': 'Bogotá',
                'state': 'Cundinamarca',
                'capacity': 1500,
                'description': 'Teatro histórico en el centro de Bogotá'
            },
            {
                'name': 'Movistar Arena',
                'address': 'Carrera 68C # 23-07',
                'city': 'Bogotá',
                'state': 'Cundinamarca',
                'capacity': 14000,
                'description': 'Arena multiusos para grandes eventos'
            },
            {
                'name': 'Centro de Convenciones',
                'address': 'Carrera 8 # 7-21',
                'city': 'Bogotá',
                'state': 'Cundinamarca',
                'capacity': 5000,
                'description': 'Centro de convenciones moderno'
            },
            {
                'name': 'Parque Simón Bolívar',
                'address': 'Calle 63',
                'city': 'Bogotá',
                'state': 'Cundinamarca',
                'capacity': 100000,
                'description': 'Parque para grandes eventos al aire libre'
            },
        ]
        
        venues = []
        for venue_data in venues_data:
            venue, created = Venue.objects.get_or_create(
                name=venue_data['name'],
                defaults=venue_data
            )
            venues.append(venue)
            if created:
                self.stdout.write(f'  ✅ {venue_data["name"]}')
        
        self.stdout.write(f'  ✅ {len(venues)} lugares creados')
        return venues

    def create_events(self, organizers, categories, venues):
        now = timezone.now()
        events_data = [
            {
                'title': 'Rock en el Parque 2025',
                'short_description': 'Festival de rock gratis',
                'description': 'El festival de rock más grande de Latinoamérica',
                'category': categories[0],  # Conciertos
                'venue': venues[3],  # Parque Simón Bolívar
                'organizer': organizers[0],  # Sarah
                'start_date': now + timedelta(days=30),
                'end_date': now + timedelta(days=30, hours=10),
                'capacity': 80000,
                'is_free': True,
                'status': 'published'
            },
            {
                'title': 'Tech Summit Colombia 2025',
                'short_description': 'Conferencia de tecnología',
                'description': 'La conferencia tech más importante del año',
                'category': categories[5],  # Tecnología
                'venue': venues[2],  # Centro de Convenciones
                'organizer': organizers[1],  # Karen
                'start_date': now + timedelta(days=15),
                'end_date': now + timedelta(days=15, hours=8),
                'capacity': 3000,
                'is_free': False,
                'status': 'published'
            },
            {
                'title': 'Festival de Jazz',
                'short_description': 'Noche de jazz en vivo',
                'description': 'Los mejores exponentes del jazz mundial',
                'category': categories[0],  # Conciertos
                'venue': venues[0],  # Teatro Colón
                'organizer': organizers[2],  # Neyireth
                'start_date': now + timedelta(days=45),
                'end_date': now + timedelta(days=45, hours=4),
                'capacity': 1200,
                'is_free': False,
                'status': 'published'
            },
            {
                'title': 'Maratón de Bogotá',
                'short_description': '42K por las calles de Bogotá',
                'description': 'Maratón internacional de Bogotá',
                'category': categories[2],  # Deportes
                'venue': venues[3],  # Parque Simón Bolívar
                'organizer': organizers[3],  # Aslhy
                'start_date': now + timedelta(days=60),
                'end_date': now + timedelta(days=60, hours=6),
                'capacity': 10000,
                'is_free': False,
                'status': 'published'
            },
        ]
        
        events = []
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                defaults=event_data
            )
            events.append(event)
            if created:
                self.stdout.write(f'  ✅ {event_data["title"]}')
        
        self.stdout.write(f'  ✅ {len(events)} eventos creados')
        return events

    def create_ticket_types(self, events):
        ticket_types_data = [
            # Tech Summit
            {
                'event': events[1],
                'name': 'Early Bird',
                'description': 'Precio especial por compra anticipada',
                'price': Decimal('150000.00'),
                'quantity': 500,
                'max_purchase': 5  # ✅ Cambio aquí
            },
            {
                'event': events[1],
                'name': 'General',
                'description': 'Acceso general al evento',
                'price': Decimal('200000.00'),
                'quantity': 2000,
                'max_purchase': 10  # ✅ Cambio aquí
            },
            {
                'event': events[1],
                'name': 'VIP',
                'description': 'Acceso VIP con networking',
                'price': Decimal('500000.00'),
                'quantity': 200,
                'max_purchase': 5  # ✅ Cambio aquí
            },
            # Jazz Festival
            {
                'event': events[2],
                'name': 'Platea',
                'description': 'Asientos en platea',
                'price': Decimal('80000.00'),
                'quantity': 800,
                'max_purchase': 6  # ✅ Cambio aquí
            },
            {
                'event': events[2],
                'name': 'Palco',
                'description': 'Palcos privados',
                'price': Decimal('150000.00'),
                'quantity': 100,
                'max_purchase': 4  # ✅ Cambio aquí
            },
            # Maratón
            {
                'event': events[3],
                'name': '42K',
                'description': 'Maratón completa',
                'price': Decimal('120000.00'),
                'quantity': 5000,
                'max_purchase': 1  # ✅ Cambio aquí
            },
            {
                'event': events[3],
                'name': '21K',
                'description': 'Media maratón',
                'price': Decimal('80000.00'),
                'quantity': 3000,
                'max_purchase': 1  # ✅ Cambio aquí
            },
        ]
        
        for ticket_data in ticket_types_data:
            TicketType.objects.get_or_create(
                event=ticket_data['event'],
                name=ticket_data['name'],
                defaults=ticket_data
            )
        
        self.stdout.write(f'  ✅ {len(ticket_types_data)} tipos de tickets creados')

    def create_sponsor_tiers(self):
        tiers_data = [
            {
                'name': 'Platinum',
                'min_amount': Decimal('20000000.00'),
                'order': 1,
                'color': '#E5E4E2',
                'benefits_description': 'Máxima visibilidad'
            },
            {
                'name': 'Gold',
                'min_amount': Decimal('10000000.00'),
                'order': 2,
                'color': '#FFD700',
                'benefits_description': 'Alta visibilidad'
            },
            {
                'name': 'Silver',
                'min_amount': Decimal('5000000.00'),
                'order': 3,
                'color': '#C0C0C0',
                'benefits_description': 'Buena visibilidad'
            },
        ]
        
        tiers = []
        for tier_data in tiers_data:
            tier, created = SponsorTier.objects.get_or_create(
                name=tier_data['name'],
                defaults=tier_data
            )
            tiers.append(tier)
            if created:
                self.stdout.write(f'  ✅ {tier_data["name"]}')
        
        self.stdout.write(f'  ✅ {len(tiers)} niveles creados')
        return tiers

    def create_sponsors(self):
        sponsors_data = [
            {
                'name': 'TechCorp Colombia',
                'industry': 'Tecnología',
                'contact_email': 'sponsor@techcorp.co',
                'status': 'active'
            },
            {
                'name': 'Banco Nacional',
                'industry': 'Finanzas',
                'contact_email': 'eventos@banco.com',
                'status': 'active'
            },
        ]
        
        sponsors = []
        for sponsor_data in sponsors_data:
            sponsor, created = Sponsor.objects.get_or_create(
                name=sponsor_data['name'],
                defaults=sponsor_data
            )
            sponsors.append(sponsor)
            if created:
                self.stdout.write(f'  ✅ {sponsor_data["name"]}')
        
        self.stdout.write(f'  ✅ {len(sponsors)} patrocinadores creados')
        return sponsors

    def create_sponsorships(self, sponsors, events, tiers):
        now = timezone.now()
        
        Sponsorship.objects.get_or_create(
            sponsor=sponsors[0],
            event=events[1],
            defaults={
                'sponsor_tier': tiers[0],
                'amount': Decimal('25000000.00'),
                'status': 'active',
                'start_date': now.date(),
                'end_date': (now + timedelta(days=90)).date()
            }
        )
        
        self.stdout.write('  ✅ 1 patrocinio creado')

    def print_summary(self):
        self.stdout.write('\n📊 RESUMEN:')
        self.stdout.write(f'  👤 Usuarios: {User.objects.count()}')
        self.stdout.write(f'  📂 Categorías: {Category.objects.count()}')
        self.stdout.write(f'  📍 Lugares: {Venue.objects.count()}')
        self.stdout.write(f'  🎪 Eventos: {Event.objects.count()}')
        self.stdout.write(f'  🎫 Tipos de Tickets: {TicketType.objects.count()}')
        self.stdout.write(f'  💎 Niveles Sponsors: {SponsorTier.objects.count()}')
        self.stdout.write(f'  🤝 Patrocinadores: {Sponsor.objects.count()}')
        
        self.stdout.write('\n🔑 CREDENCIALES:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Organizadores: sarah, karen, neyireth, aslhy / [nombre]123')
        self.stdout.write('  Usuarios: user1-5 / user123')