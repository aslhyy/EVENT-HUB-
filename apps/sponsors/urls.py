"""
URLs para patrocinadores.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SponsorTierViewSet, SponsorViewSet,
    SponsorshipViewSet, SponsorBenefitViewSet
)

router = DefaultRouter()
router.register(r'tiers', SponsorTierViewSet, basename='sponsor-tier')
router.register(r'benefits', SponsorBenefitViewSet, basename='sponsor-benefit')
router.register(r'sponsorships', SponsorshipViewSet, basename='sponsorship')
router.register(r'', SponsorViewSet, basename='sponsor')

urlpatterns = [
    path('', include(router.urls)),
]