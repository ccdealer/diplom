# ameneties/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoodsViewSet, ServicesViewSet

app_name = 'ameneties'

router = DefaultRouter()
router.register(r'goods', GoodsViewSet, basename='goods')
router.register(r'services', ServicesViewSet, basename='services')

urlpatterns = [
    path('', include(router.urls)),
]