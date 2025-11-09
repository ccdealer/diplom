# documentation/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NationalityViewSet, DocumentViewSet

app_name = 'documentation'

router = DefaultRouter()
router.register(r'nationalities', NationalityViewSet, basename='nationality')
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    path('', include(router.urls)),
]