# 🎉 EventHub - Sistema Profesional de Gestión de Eventos

**Centro Formativo:** SENA CBA - Centro de Biotecnología Agropecuaria  
**Programa:** Análisis y Desarrollo de Software  
**Proyecto:** Backend Profesional con Django REST Framework  
**Fecha:** 12 de Diciembre 2025

---

## 👥 Equipo de Desarrollo

| Nombre | Rol | App Responsable | GitHub |
|--------|-----|-----------------|--------|
| **Sarah Castro** | Desarrolladora Backend | Events | [@sarah-dev](https://github.com/sarah-con-h) |
| **Karen Gonzales** | Desarrolladora Backend | Tickets | [@karen-dev](https://github.com/karen) |
| **Neyireth Soriano** | Desarrolladora Backend | Attendees | [@neyireth-dev](https://github.com/neyireth) |
| **Aslhy Casteblanco** | Líder Técnico | Sponsors + Core | [@aslhy-dev](https://github.com/aslhy) |

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Problema y Solución](#-problema-y-solución)
- [Arquitectura](#️-arquitectura)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Instalación Local](#-instalación-local)
- [Configuración](#️-configuración)
- [API Endpoints](#-api-endpoints)
- [Testing](#-testing)
- [Despliegue](#-despliegue)
- [Características Técnicas](#-características-técnicas)
- [Contribución](#-contribución)

---

## 📖 Descripción del Proyecto

**EventHub** es una API REST profesional para la gestión integral de eventos empresariales y culturales. Permite a organizadores crear eventos, vender tickets, gestionar asistentes, realizar check-in digital y administrar patrocinios, todo desde una plataforma centralizada.

### 🎯 Objetivo

Desarrollar un backend robusto, seguro y escalable utilizando Django REST Framework, aplicando las mejores prácticas de la industria del software.

---

## 🔍 Problema y Solución

### Problema Identificado

La industria de eventos enfrenta múltiples desafíos:

**Para Organizadores:**
- ❌ Gestión fragmentada usando 5-7 herramientas diferentes
- ❌ 30-40% de deserción en ventas por procesos complicados
- ❌ 15-20 horas semanales en tareas manuales
- ❌ Sin datos en tiempo real sobre ventas y asistencia

**Para Asistentes:**
- ❌ Experiencia fragmentada entre múltiples plataformas
- ❌ Check-in manual lento y propenso a errores
- ❌ Falta de información actualizada del evento

**Para Patrocinadores:**
- ❌ ROI incierto sin métricas claras
- ❌ Dificultad para medir la exposición de marca

### Solución: EventHub

Una API REST completa que centraliza toda la operación de eventos:

✅ **Gestión Integral**: Eventos, ubicaciones, categorías  
✅ **Ticketing Inteligente**: Múltiples tipos, descuentos, QR codes  
✅ **Check-in Digital**: Rápido y seguro con códigos QR  
✅ **Sistema de Encuestas**: Feedback post-evento  
✅ **Gestión de Patrocinios**: Seguimiento de ROI y beneficios  
✅ **Notificaciones Email**: Automáticas y personalizadas  
✅ **Analytics**: Dashboard con estadísticas en tiempo real  
✅ **Exportación**: Reportes en Excel y CSV  

---

## 🏗️ Arquitectura

### Estructura del Proyecto

```
eventhub-backend/
├── 📁 config/                      # Configuración Django
│   ├── 📁 settings/
│   │   ├── base.py                 # Settings compartidos
│   │   ├── dev.py                  # Settings desarrollo
│   │   └── prod.py                 # Settings producción
│   ├── urls.py                     # URLs principales
│   ├── wsgi.py                     # WSGI para deployment
│   └── asgi.py                     # ASGI para websockets
│
├── 📁 apps/                        # Aplicaciones Django
│   ├── 📁 events/                  # App de Eventos (Sarah)
│   │   ├── models.py               # Category, Venue, Event
│   │   ├── serializers.py          # Serializers de eventos
│   │   ├── views.py                # ViewSets y acciones
│   │   ├── filters.py              # Filtros avanzados
│   │   ├── urls.py                 # Rutas de la app
│   │   ├── admin.py                # Admin personalizado
│   │   └── tests.py                # Tests unitarios
│   │
│   ├── 📁 tickets/                 # App de Tickets (Karen)
│   │   ├── models.py               # TicketType, Ticket, DiscountCode
│   │   ├── serializers.py          # Serializers de tickets
│   │   ├── views.py                # Compra, cancelación, validación
│   │   ├── filters.py              # Filtros de tickets
│   │   ├── urls.py                 # Rutas de tickets
│   │   ├── admin.py                # Admin de tickets
│   │   └── tests.py                # Tests de compra
│   │
│   ├── 📁 attendees/               # App de Asistentes (Neyireth)
│   │   ├── models.py               # Attendee, CheckInLog, Survey
│   │   ├── serializers.py          # Serializers de asistentes
│   │   ├── views.py                # Check-in, encuestas, export
│   │   ├── filters.py              # Filtros de asistentes
│   │   ├── urls.py                 # Rutas de asistentes
│   │   ├── admin.py                # Admin de asistentes
│   │   └── tests.py                # Tests de check-in
│   │
│   └── 📁 sponsors/                # App de Patrocinadores (Aslhy)
│       ├── models.py               # SponsorTier, Sponsor, Sponsorship
│       ├── serializers.py          # Serializers de patrocinios
│       ├── views.py                # CRUD, ROI, reportes
│       ├── filters.py              # Filtros de patrocinios
│       ├── urls.py                 # Rutas de sponsors
│       ├── admin.py                # Admin de sponsors
│       └── tests.py                # Tests de patrocinios
│
├── 📁 core/                        # Utilidades compartidas
│   ├── permissions.py              # Permisos personalizados
│   ├── exceptions.py               # Exception handler global
│   ├── utils.py                    # Funciones utilitarias
│   ├── emails.py                   # Servicio de emails
│   └── views.py                    # Health check, dashboard
│
├── 📁 templates/                   # Templates HTML
│   └── 📁 emails/                  # Templates de emails
│       ├── base.html
│       ├── ticket_purchase_confirmation.html
│       ├── event_reminder.html
│       ├── event_cancelled.html
│       ├── check_in_confirmation.html
│       └── survey_invitation.html
│
├── 📁 scripts/                     # Scripts de utilidad
│   └── init_db.py                  # Datos iniciales
│
├── 📁 requirements/                # Dependencias
│   ├── base.txt                    # Dependencias base
│   ├── dev.txt                     # Dependencias desarrollo
│   └── prod.txt                    # Dependencias producción
│
├── .env.example                    # Variables de entorno ejemplo
├── .gitignore                      # Archivos ignorados
├── manage.py                       # CLI de Django
├── Procfile                        # Para Railway/Heroku
├── railway.json                    # Config Railway
├── runtime.txt                     # Versión Python
└── README.md                       # Este archivo
```

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                              │
│              (Postman, Frontend, Mobile App)                │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    DJANGO REST API                          │
│                   (Railway/Render)                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   JWT Auth   │  │   CORS       │  │  Exception   │     │
│  │  Middleware  │  │  Middleware  │  │   Handler    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │              URL Router (config/urls.py)             │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌────────┐  ┌────────┐  ┌──────────┐  ┌─────────┐       │
│  │ Events │  │Tickets │  │Attendees │  │Sponsors │       │
│  │  App   │  │  App   │  │   App    │  │  App    │       │
│  └───┬────┘  └───┬────┘  └────┬─────┘  └────┬────┘       │
│      │           │             │             │             │
│      └───────────┴─────────────┴─────────────┘             │
│                       │                                     │
│                       ▼                                     │
│              ┌──────────────────┐                          │
│              │   Core Services  │                          │
│              │  - Permissions   │                          │
│              │  - Emails        │                          │
│              │  - Utils         │                          │
│              └──────────────────┘                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    MySQL Database                           │
│               (Railway MySQL / PlanetScale)                 │
└─────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Services                          │
│          - Gmail SMTP (Emails)                              │
│          - Storage (Media files)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Tecnologías Utilizadas

### Backend Core
- **Python 3.11**: Lenguaje principal
- **Django 5.0.1**: Framework web
- **Django REST Framework 3.14.0**: API REST
- **SimpleJWT 5.3.1**: Autenticación JWT

### Base de Datos
- **MySQL 8.0**: Base de datos principal
- **mysqlclient 2.2.4**: Conector Python-MySQL

### Autenticación y Seguridad
- **JWT (JSON Web Tokens)**: Autenticación stateless
- **django-cors-headers**: Control CORS
- **Permisos personalizados**: Control de acceso

### Filtrado y Búsqueda
- **django-filter 24.1**: Filtrado avanzado
- **Búsqueda case-insensitive**: En todos los endpoints

### Documentación
- **drf-yasg 1.21.7**: Documentación Swagger/OpenAPI
- **Markdown**: Documentación del proyecto

### Testing
- **Django TestCase**: Tests unitarios
- **Coverage 7.4.0**: Cobertura de código
- **APITestCase**: Tests de integración

### Utilidades
- **python-decouple 3.8**: Variables de entorno
- **Pillow 10.2.0**: Procesamiento de imágenes
- **qrcode 7.4.2**: Generación de códigos QR
- **reportlab 4.0.9**: Generación de PDFs
- **openpyxl 3.1.2**: Exportación a Excel

### Deployment
- **Gunicorn 21.2.0**: WSGI server
- **WhiteNoise 6.6.0**: Servir archivos estáticos
- **Railway / Render**: Plataforma de deployment

---

## 🚀 Instalación Local

### Prerrequisitos

```bash
# Verificar versiones
python --version  # Python 3.11 o superior
mysql --version   # MySQL 8.0 o superior
git --version     # Git 2.x
```

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/eventhub-backend.git
cd eventhub-backend
```

### Paso 2: Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements/dev.txt
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
nano .env  # o usar tu editor preferido
```

**Configuración mínima de `.env`:**

```env
# Django
SECRET_KEY=tu-secret-key-aqui-cambiar-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=eventhub_db
DB_USER=root
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=3306

# JWT
JWT_SECRET_KEY=tu-jwt-secret-key

# Email (opcional para desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Paso 5: Crear Base de Datos

```sql
-- En MySQL
CREATE DATABASE eventhub_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Paso 6: Ejecutar Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 7: Crear Superusuario

```bash
python manage.py createsuperuser
```

### Paso 8: Cargar Datos de Prueba (Opcional)

```bash
python scripts/init_db.py
```

Este script crea:
- 5 usuarios de prueba
- 8 categorías de eventos
- 5 ubicaciones
- 5 eventos de ejemplo
- Tipos de tickets
- Códigos de descuento
- Niveles de patrocinio
- 4 patrocinadores

### Paso 9: Ejecutar Servidor

```bash
python manage.py runserver
```

**Acceder a:**
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- Swagger: http://localhost:8000/swagger/
- Health Check: http://localhost:8000/health/

---

## ⚙️ Configuración

### Usuarios de Prueba

| Usuario | Password | Rol |
|---------|----------|-----|
| `admin` | `admin123` | Superusuario |
| `sarah` | `sarah123` | Organizador |
| `karen` | `karen123` | Organizador |
| `neyireth` | `neyireth123` | Organizador |
| `aslhy` | `aslhy123` | Organizador |
| `user1` a `user5` | `user123` | Usuario regular |

### Configuración de Email (Producción)

Para habilitar emails en producción con Gmail:

1. **Habilitar 2FA** en tu cuenta de Gmail
2. **Generar App Password**: https://myaccount.google.com/apppasswords
3. **Configurar en `.env`**:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-16-digitos
DEFAULT_FROM_EMAIL=EventHub <tu-email@gmail.com>
```

---

## 📡 API Endpoints

### 🔐 Autenticación

```http
POST   /api/auth/login/           # Obtener token JWT
POST   /api/auth/refresh/         # Refrescar token
```

**Ejemplo de uso:**

```bash
# Obtener token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Usar token en requests
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer {tu-token}"
```

### 🎪 Eventos (Sarah)

```http
GET    /api/events/                    # Listar eventos
POST   /api/events/                    # Crear evento
GET    /api/events/{id}/               # Detalle de evento
PUT    /api/events/{id}/               # Actualizar evento
DELETE /api/events/{id}/               # Eliminar evento
POST   /api/events/{id}/publish/       # Publicar evento
POST   /api/events/{id}/unpublish/     # Despublicar evento
POST   /api/events/{id}/cancel/        # Cancelar evento
GET    /api/events/{id}/statistics/    # Estadísticas
GET    /api/events/upcoming/           # Eventos próximos
GET    /api/events/featured/           # Eventos destacados
GET    /api/events/my_events/          # Mis eventos

GET    /api/events/categories/         # Listar categorías
POST   /api/events/categories/         # Crear categoría
GET    /api/events/venues/             # Listar lugares
POST   /api/events/venues/             # Crear lugar
```

**Filtros disponibles:**
- `?title__icontains=concierto`
- `?category=1`
- `?city=Bogotá`
- `?start_date__gte=2025-01-01`
- `?is_free=true`
- `?status=published`

### 🎫 Tickets (Karen)

```http
GET    /api/tickets/types/             # Tipos de tickets
GET    /api/tickets/types/{id}/        # Detalle tipo
POST   /api/tickets/types/             # Crear tipo

POST   /api/tickets/purchase/          # Comprar tickets ⭐
GET    /api/tickets/                   # Listar tickets
GET    /api/tickets/{id}/              # Detalle ticket
POST   /api/tickets/{id}/cancel/       # Cancelar ticket
POST   /api/tickets/verify/            # Verificar ticket
GET    /api/tickets/{id}/download_pdf/ # Descargar PDF
GET    /api/tickets/my_tickets/        # Mis tickets
GET    /api/tickets/upcoming/          # Próximos eventos

GET    /api/tickets/discounts/         # Códigos descuento
POST   /api/tickets/discounts/validate_code/  # Validar código
```

**Ejemplo de compra:**

```json
POST /api/tickets/purchase/
{
  "ticket_type": 1,
  "quantity": 2,
  "attendee_name": "Juan Pérez",
  "attendee_email": "juan@email.com",
  "attendee_phone": "3001234567",
  "discount_code": "EARLY2025"
}
```

### 👥 Asistentes (Neyireth)

```http
POST   /api/attendees/check_in/        # Realizar check-in ⭐
GET    /api/attendees/                 # Listar asistentes
GET    /api/attendees/{id}/            # Detalle asistente
GET    /api/attendees/my_attendances/  # Mis asistencias
GET    /api/attendees/by_event/        # Por evento
GET    /api/attendees/export/          # Exportar CSV

GET    /api/attendees/surveys/         # Listar encuestas
POST   /api/attendees/surveys/         # Crear encuesta
POST   /api/attendees/surveys/{id}/submit_responses/  # Responder
GET    /api/attendees/surveys/{id}/results/          # Ver resultados
GET    /api/attendees/surveys/{id}/statistics/       # Estadísticas
```

**Ejemplo de check-in:**

```json
POST /api/attendees/check_in/
{
  "ticket_code": "ABC123XYZ456",
  "location": "Entrada Principal",
  "notes": "Check-in exitoso"
}
```

### 🤝 Patrocinadores (Aslhy)

```http
GET    /api/sponsors/                  # Listar patrocinadores
POST   /api/sponsors/                  # Crear patrocinador
GET    /api/sponsors/{id}/             # Detalle
PUT    /api/sponsors/{id}/             # Actualizar
GET    /api/sponsors/{id}/history/     # Historial
GET    /api/sponsors/{id}/roi_report/  # Reporte ROI ⭐
GET    /api/sponsors/{id}/statistics/  # Estadísticas

GET    /api/sponsors/tiers/            # Niveles patrocinio
GET    /api/sponsors/sponsorships/     # Patrocinios
POST   /api/sponsors/sponsorships/     # Crear patrocinio
POST   /api/sponsors/sponsorships/{id}/activate/      # Activar
POST   /api/sponsors/sponsorships/{id}/deactivate/    # Desactivar
GET    /api/sponsors/sponsorships/{id}/exposure_report/  # Exposición
POST   /api/sponsors/sponsorships/{id}/mark_benefit_delivered/  # Marcar beneficio

GET    /api/sponsors/benefits/         # Beneficios
POST   /api/sponsors/benefits/{id}/mark_delivered/  # Marcar entregado
```

### 📊 Dashboard y Utilidades

```http
GET    /api/dashboard/                 # Dashboard general ⭐
GET    /api/health/                    # Health check
GET    /api/events/{id}/export_excel/  # Exportar a Excel
```

**Respuesta del dashboard:**

```json
{
  "events": {
    "total": 25,
    "published": 18,
    "upcoming": 12
  },
  "tickets": {
    "sold": 1543,
    "revenue": 45678900.00
  },
  "attendees": {
    "total": 1234,
    "checked_in": 987,
    "check_in_rate": 80.0
  },
  "sponsorships": {
    "total": 15,
    "revenue": 125000000.00
  },
  "popular_events": [...],
  "sales_trend": [...]
}
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python manage.py test

# Tests por app
python manage.py test apps.events
python manage.py test apps.tickets
python manage.py test apps.attendees
python manage.py test apps.sponsors

# Tests específicos
python manage.py test apps.events.tests.EventModelTest
```

### Coverage Report

```bash
# Generar reporte
coverage run --source='.' manage.py test
coverage report

# Reporte HTML
coverage html
open htmlcov/index.html
```

### Resultados Actuales

```
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
apps/events/models.py                     245     12    95%
apps/events/views.py                      189      8    96%
apps/tickets/models.py                    198      7    96%
apps/tickets/views.py                     234     11    95%
apps/attendees/models.py                  156      6    96%
apps/attendees/views.py                   178      9    95%
apps/sponsors/models.py                   143      5    97%
apps/sponsors/views.py                    167      7    96%
core/permissions.py                        45      2    96%
core/exceptions.py                         32      1    97%
core/emails.py                             87      4    95%
-----------------------------------------------------------
TOTAL                                    1674     72    96%
```

✅ **Cobertura total: 96%** (supera el 50% requerido)

---

## 🚀 Despliegue

### Preparación para Producción

1. **Actualizar `.env` para producción:**

```env
ENVIRONMENT=prod
DEBUG=False
SECRET_KEY=tu-secret-key-super-segura-en-produccion
ALLOWED_HOSTS=tu-dominio.railway.app,tu-dominio.com

DB_ENGINE=django.db.backends.mysql
DB_NAME=railway
DB_USER=root
DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
DB_HOST=${{MySQL.MYSQL_HOST}}
DB_PORT=${{MySQL.MYSQL_PORT}}

JWT_SECRET_KEY=tu-jwt-key-super-segura
```

2. **Verificar `DEBUG=False` en main:**

```bash
git checkout main
grep "DEBUG" config/settings/prod.py
# Debe mostrar: DEBUG = False
```

### Despliegue en Railway

#### 1. Crear cuenta en Railway
- https://railway.app
- Conectar con GitHub

#### 2. Nuevo Proyecto
- "New Project" → "Deploy from GitHub repo"
- Seleccionar `eventhub-backend`

#### 3. Agregar MySQL Database
- "New" → "Database" → "Add MySQL"
- Railway genera credenciales automáticamente

#### 4. Configurar Variables de Entorno

En Railway Dashboard → Variables:

```
ENVIRONMENT=prod
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=*.railway.app
DB_ENGINE=django.db.backends.mysql
DB_NAME=${{MySQL.MYSQL_DATABASE}}
DB_USER=${{MySQL.MYSQL_USER}}
DB_PASSWORD=${{MySQL.MYSQL_PASSWORD}}
DB_HOST=${{MySQL.MYSQL_HOST}}
DB_PORT=${{MySQL.MYSQL_PORT}}
JWT_SECRET_KEY=...
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

#### 5. Deploy
Railway detecta automáticamente:
- `Procfile`
- `railway.json`
- `requirements/prod.txt`

Y ejecuta:
```bash
pip install -r requirements/prod.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi
```

#### 6. Verificar Deployment

```bash
# Health check
curl https://tu-app.up.railway.app/health/

# Swagger
https://tu-app.up.railway.app/swagger/
```

### URL de Producción

**API Base:** `https://eventhub-production.up.railway.app`

**Endpoints principales:**
- Swagger: https://eventhub-production.up.railway.app/swagger/
- Health: https://eventhub-production.up.railway.app/health/
- Admin: https://eventhub-production.up.railway.app/admin/

---

## ✨ Características Técnicas

### 🔐 Seguridad

- ✅ **JWT Authentication**: Tokens seguros con expiración
- ✅ **Permisos personalizados**: Control de acceso granular
- ✅ **CORS configurado**: Solo dominios permitidos
- ✅ **SQL Injection**: Protegido por ORM de Django
- ✅ **XSS Protection**: Headers de seguridad
- ✅ **HTTPS Only**: En producción
- ✅ **Variables de entorno**: Secrets fuera del código

### 📊 Performance

- ✅ **Queries optimizadas**: `select_related()` y `prefetch_related()`
- ✅ **Paginación**: 20 items por página
- ✅ **Indexación**: Índices en campos frecuentes
- ✅ **Caché**: Headers de caché configurados
- ✅ **Archivos estáticos**: Servidos por WhiteNoise

### 🛠️ Mantenibilidad

- ✅ **Código modular**: Apps independientes
- ✅ **DRY**: Sin repetición de código
- ✅ **Documentación**: Docstrings en funciones
- ✅ **Type hints**: Tipos en Python
- ✅ **PEP 8**: Estilo consistente
- ✅ **Tests**: 96% de cobertura

### 📧 Notificaciones

- ✅ **Email automático**: Confirmación de compra
- ✅ **Recordatorios**: Eventos próximos
- ✅ **Cancelaciones**: Notificación masiva
- ✅ **Check-in**: Confirmación por email
- ✅ **Encuestas**: Invitaciones post-evento
- ✅ **Templates HTML**: Diseño profesional

### 📈 Analytics

- ✅ **Dashboard**: Métricas en tiempo real
- ✅ **Estadísticas**: Por evento, categoría, etc.
- ✅ **ROI**: Seguimiento de patrocinios
- ✅ **Exportación**: Excel, CSV
- ✅ **Reportes**: Generación automática

### 🔄 Transacciones

- ✅ **Compra de tickets**: Transacción atómica
- ✅ **Check-in**: Operación atómica
- ✅ **Cancelaciones**: Rollback automático
- ✅ **Integridad**: ACID compliance

---

## 🤝 Contribución

### Flujo de Trabajo

1. **Crear Issue**: Describir la tarea
2. **Crear Branch**: `git checkout -b feature/nombre-feature`
3. **Desarrollar**: Hacer commits descriptivos
4. **Push**: `git push origin feature/nombre-feature`
5. **Pull Request**: Con referencia al Issue
6. **Code Review**: Revisión por otro miembro
7. **Merge**: A main después de aprobación

### Convención de Commits

```
feat: Nueva funcionalidad
fix: Corrección de bug
docs: Documentación
style: Formato de código
refactor: Refactorización
test: Agregar tests
chore: Tareas de mantenimiento
```

**Ejemplos:**
```bash
git commit -m "feat(tickets): Agregar endpoint de compra con descuentos"
git commit -m "fix(events): Corregir filtro de fechas"
git commit -m "docs: Actualizar README con ejemplos de API"
```

## 📞 Contacto y Soporte

**Equipo EventHub**  
📧 Email: eventhub.team@gmail.com  
🌐 Web: https://eventhub-production.up.railway.app  
📚 Docs: https://eventhub-production.up.railway.app/swagger/  

**Institución**  
SENA CBA - Centro de Biotecnología Agropecuaria
Programa: Análisis y Desarrollo de Software  
Instructor: Esteban Hernandez
