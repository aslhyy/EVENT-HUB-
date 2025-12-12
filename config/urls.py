"""
URLs principales de EventHub.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import dashboard_stats, health_check

# Configuración de Swagger con JWT
schema_view = get_schema_view(
    openapi.Info(
        title="EventHub API",
        default_version='v1',
        description="""
# 🎉 EventHub API - Sistema Profesional de Gestión de Eventos

API REST completa para gestión de eventos, tickets, asistentes y patrocinios.

## 🔐 Autenticación

Esta API utiliza **JWT (JSON Web Tokens)** para autenticación.

### Cómo autenticarte:

1. **Obtén un token**: 
   - Endpoint: `POST /api/auth/login/`
   - Body: `{"username": "admin", "password": "admin123"}`

2. **Copia el token `access`** de la respuesta

3. **Autorízate en Swagger**:
   - Click en el botón **"Authorize"** 🔓 (arriba a la derecha)
   - En el campo **"Value"**, escribe: `Bearer {tu-token}`
   - Ejemplo: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Click en **"Authorize"** y luego **"Close"**

4. **¡Listo!** Ahora todos los endpoints funcionarán

### Usuarios de prueba:
- **Admin**: `admin` / `admin123`
- **Organizadores**: `sarah`, `karen`, `neyireth`, `aslhy` / `{nombre}123`
- **Usuarios**: `user1` a `user5` / `user123`

## 📚 Características

- ✅ Gestión completa de eventos
- 🎫 Sistema de ticketing con QR
- 👥 Check-in de asistentes
- 🤝 Gestión de patrocinios
- 📧 Notificaciones por email
- 📊 Dashboard con estadísticas
- 📥 Exportación a Excel/CSV

---
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@eventhub.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    # 👇 CONFIGURACIÓN JWT PARA SWAGGER
    authentication_classes=[],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health Check
    path('health/', health_check, name='health_check'),
    path('api/health/', health_check, name='api_health_check'),
    
    # Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Apps
    path('api/events/', include('apps.events.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/attendees/', include('apps.attendees.urls')),
    path('api/sponsors/', include('apps.sponsors.urls')),
    
    # Dashboard
    path('api/dashboard/', dashboard_stats, name='dashboard_stats'),
    
    # Swagger Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Personalizar admin
admin.site.site_header = "EventHub Admin"
admin.site.site_title = "EventHub Admin Portal"
admin.site.index_title = "Bienvenido a EventHub Administration"