# booking/urls.py (продолжение)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AgentViewSet, GuestViewSet, RoomTypeViewSet, RoomViewSet,
    RoomConditionViewSet, BookingViewSet, BookingCardViewSet
)

app_name = 'booking'

router = DefaultRouter()
router.register(r'agents', AgentViewSet, basename='agent')
router.register(r'guests', GuestViewSet, basename='guest')
router.register(r'room-types', RoomTypeViewSet, basename='roomtype')
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'room-conditions', RoomConditionViewSet, basename='roomcondition')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'booking-cards', BookingCardViewSet, basename='bookingcard')

urlpatterns = [
    path('', include(router.urls)),
]