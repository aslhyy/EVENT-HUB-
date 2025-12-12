"""
URLs para asistentes.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendeeViewSet, SurveyViewSet

router = DefaultRouter()
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'', AttendeeViewSet, basename='attendee')

urlpatterns = [
    path('', include(router.urls)),
]