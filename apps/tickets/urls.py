"""
URLs para tickets.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketTypeViewSet, TicketViewSet, DiscountCodeViewSet

router = DefaultRouter()
router.register(r'types', TicketTypeViewSet, basename='ticket-type')
router.register(r'discounts', DiscountCodeViewSet, basename='discount-code')
router.register(r'', TicketViewSet, basename='ticket')

urlpatterns = [
    path('', include(router.urls)),
]