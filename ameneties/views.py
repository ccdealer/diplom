# ameneties/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .models import Goods, Services
from .serializers import (
    GoodsListSerializer, GoodsDetailSerializer, GoodsCreateUpdateSerializer,
    ServicesListSerializer, ServicesDetailSerializer, ServicesCreateUpdateSerializer
)


class GoodsViewSet(viewsets.ModelViewSet):
    """
    ViewSet для товаров
    
    list: Список всех товаров
    retrieve: Детали конкретного товара
    create: Создать новый товар
    update: Обновить товар
    partial_update: Частично обновить товар
    destroy: Удалить товар
    """
    queryset = Goods.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'price']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GoodsListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GoodsCreateUpdateSerializer
        return GoodsDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список товаров",
        operation_description="Получить все товары с возможностью поиска"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать товар",
        operation_description="Создать новый товар"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Детали товара",
        operation_description="Получить детальную информацию о товаре"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Обновить товар",
        operation_description="Полностью обновить товар"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Частично обновить товар",
        operation_description="Частично обновить товар"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Удалить товар",
        operation_description="Удалить товар"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Актуальные товары",
        operation_description="Получить товары, актуальные на текущую дату"
    )
    @action(detail=False, methods=['get'])
    def relevant(self, request):
        """Актуальные товары"""
        today = timezone.now().date()
        goods = self.get_queryset().filter(
            relevant_from__lte=today,
            relevant_to__gte=today
        )
        serializer = GoodsListSerializer(goods, many=True)
        return Response({
            'count': goods.count(),
            'goods': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Статистика по товарам",
        operation_description="Общая статистика по товарам"
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по товарам"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        total_count = queryset.count()
        relevant_count = queryset.filter(
            relevant_from__lte=today,
            relevant_to__gte=today
        ).count()
        
        total_price = sum(g.price for g in queryset)
        avg_price = total_price / total_count if total_count > 0 else 0
        max_price = max((g.price for g in queryset), default=0)
        min_price = min((g.price for g in queryset), default=0)
        
        return Response({
            'total_goods': total_count,
            'relevant_goods': relevant_count,
            'total_price': total_price,
            'average_price': round(avg_price, 2),
            'max_price': max_price,
            'min_price': min_price
        })


class ServicesViewSet(viewsets.ModelViewSet):
    """
    ViewSet для услуг
    
    list: Список всех услуг
    retrieve: Детали конкретной услуги
    create: Создать новую услугу
    update: Обновить услугу
    partial_update: Частично обновить услугу
    destroy: Удалить услугу
    """
    queryset = Services.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['id', 'name', 'price']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ServicesListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ServicesCreateUpdateSerializer
        return ServicesDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список услуг",
        operation_description="Получить все услуги с возможностью поиска"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать услугу",
        operation_description="Создать новую услугу"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Детали услуги",
        operation_description="Получить детальную информацию об услуге"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Обновить услугу",
        operation_description="Полностью обновить услугу"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Частично обновить услугу",
        operation_description="Частично обновить услугу"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Удалить услугу",
        operation_description="Удалить услугу"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Актуальные услуги",
        operation_description="Получить услуги, актуальные на текущую дату"
    )
    @action(detail=False, methods=['get'])
    def relevant(self, request):
        """Актуальные услуги"""
        today = timezone.now().date()
        services = self.get_queryset().filter(
            relevant_from__lte=today,
            relevant_to__gte=today
        )
        serializer = ServicesListSerializer(services, many=True)
        return Response({
            'count': services.count(),
            'services': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Статистика по услугам",
        operation_description="Общая статистика по услугам"
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по услугам"""
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        total_count = queryset.count()
        relevant_count = queryset.filter(
            relevant_from__lte=today,
            relevant_to__gte=today
        ).count()
        
        total_price = sum(s.price for s in queryset)
        avg_price = total_price / total_count if total_count > 0 else 0
        max_price = max((s.price for s in queryset), default=0)
        min_price = min((s.price for s in queryset), default=0)
        
        return Response({
            'total_services': total_count,
            'relevant_services': relevant_count,
            'total_price': total_price,
            'average_price': round(avg_price, 2),
            'max_price': max_price,
            'min_price': min_price
        })