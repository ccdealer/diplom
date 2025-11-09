from django.shortcuts import render

# Create your views here.
# documentation/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from datetime import timedelta

from .models import Nationality, Document
from .serializers import (
    NationalitySerializer,
    DocumentListSerializer,
    DocumentDetailSerializer,
    DocumentCreateUpdateSerializer
)


class NationalityViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления национальностями/гражданствами
    
    list: Получить список всех национальностей
    retrieve: Получить детали конкретной национальности
    create: Создать новую национальность
    update: Обновить национальность
    partial_update: Частично обновить национальность
    destroy: Удалить национальность
    """
    queryset = Nationality.objects.all()
    serializer_class = NationalitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nationality', 'code']
    ordering_fields = ['nationality', 'code']
    ordering = ['nationality']
    
    @swagger_auto_schema(
        operation_summary="Список национальностей",
        operation_description="Возвращает список всех национальностей с количеством документов и гостей",
        responses={200: NationalitySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать национальность",
        operation_description="Создать новую национальность/гражданство",
        request_body=NationalitySerializer,
        responses={
            201: NationalitySerializer(),
            400: "Неверные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Документы по национальности",
        operation_description="Получить все документы для конкретной национальности",
        responses={200: DocumentListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Получить все документы для национальности"""
        nationality = self.get_object()
        documents = nationality.documents.all()
        serializer = DocumentListSerializer(documents, many=True)
        return Response(serializer.data)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления документами гостей
    
    Управление паспортами, удостоверениями личности и другими документами гостей
    """
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nationality', 'document_type']  # ✅ УБРАНО 'is_expired'
    search_fields = ['IIN', 'first_name', 'last_name', 'middle_name', 'number']
    ordering_fields = ['uploaded_at', 'expiry_date', 'last_name', 'first_name']
    ordering = ['-uploaded_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DocumentCreateUpdateSerializer
        return DocumentDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список документов",
        operation_description="Возвращает список всех документов с возможностью фильтрации и поиска",
        manual_parameters=[
            openapi.Parameter(
                'nationality',
                openapi.IN_QUERY,
                description="ID национальности для фильтрации",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'document_type',
                openapi.IN_QUERY,
                description="Тип документа (passport, id_card)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Поиск по ИИН, ФИО, номеру документа",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={200: DocumentListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать документ",
        operation_description="Создать новый документ гостя с автоматической валидацией ИИН и дат",
        request_body=DocumentCreateUpdateSerializer,
        responses={
            201: DocumentDetailSerializer(),
            400: "Ошибка валидации"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Истекающие документы",
        operation_description="Возвращает список документов, срок действия которых истекает в ближайшие N дней",
        manual_parameters=[
            openapi.Parameter(
                'days',
                openapi.IN_QUERY,
                description="Количество дней (по умолчанию 30)",
                type=openapi.TYPE_INTEGER,
                default=30
            )
        ],
        responses={200: DocumentListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Документы, срок действия которых истекает скоро"""
        days = int(request.query_params.get('days', 30))
        today = timezone.now().date()
        expiry_date = today + timedelta(days=days)
        
        documents = self.get_queryset().filter(
            expiry_date__gt=today,
            expiry_date__lte=expiry_date
        ).order_by('expiry_date')
        
        serializer = DocumentListSerializer(documents, many=True)
        return Response({
            'count': documents.count(),
            'days': days,
            'documents': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Просроченные документы",
        operation_description="Возвращает список документов с истёкшим сроком действия",
        responses={200: DocumentListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Просроченные документы"""
        today = timezone.now().date()
        documents = self.get_queryset().filter(
            expiry_date__lt=today
        ).order_by('expiry_date')
        
        serializer = DocumentListSerializer(documents, many=True)
        return Response({
            'count': documents.count(),
            'documents': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Поиск по ИИН",
        operation_description="Найти документ по ИИН (12 цифр)",
        manual_parameters=[
            openapi.Parameter(
                'iin',
                openapi.IN_QUERY,
                description="ИИН (12 цифр)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: DocumentDetailSerializer(),
            404: "Документ не найден",
            400: "Неверный формат ИИН"
        }
    )
    @action(detail=False, methods=['get'])
    def by_iin(self, request):
        """Поиск документа по ИИН"""
        iin = request.query_params.get('iin')
        
        if not iin:
            return Response(
                {'error': 'Укажите параметр iin'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Валидация формата ИИН
        if not iin.isdigit() or len(iin) != 12:
            return Response(
                {'error': 'ИИН должен содержать ровно 12 цифр'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            document = self.get_queryset().get(IIN=iin)
            serializer = DocumentDetailSerializer(document)
            return Response(serializer.data)
        except Document.DoesNotExist:
            return Response(
                {'error': f'Документ с ИИН {iin} не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_summary="Статистика по документам",
        operation_description="Общая статистика по всем документам",
        responses={
            200: openapi.Response(
                description="Статистика",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'by_type': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'expired': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'expiring_soon': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'valid': openapi.Schema(type=openapi.TYPE_INTEGER),
                    }
                )
            )
        }
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика по документам"""
        from django.db.models import Count, Q
        
        queryset = self.get_queryset()
        today = timezone.now().date()
        
        # Общее количество
        total = queryset.count()
        
        # По типам
        by_type = {}
        for doc_type, label in Document.DOCUMENT_TYPES:
            count = queryset.filter(document_type=doc_type).count()
            by_type[label] = count
        
        # Просроченные
        expired = queryset.filter(expiry_date__lt=today).count()
        
        # Истекают в ближайшие 30 дней
        expiring_soon = queryset.filter(
            expiry_date__gt=today,
            expiry_date__lte=today + timedelta(days=30)
        ).count()
        
        # Действительные
        valid = queryset.filter(
            Q(expiry_date__gte=today) | Q(expiry_date__isnull=True)
        ).count()
        
        return Response({
            'total': total,
            'by_type': by_type,
            'expired': expired,
            'expiring_soon': expiring_soon,
            'valid': valid
        })
    
    @swagger_auto_schema(
    operation_summary="Проверить документ",
    operation_description="Проверить валидность документа (срок действия, корректность данных)",
    responses={
        200: openapi.Response(
            description="Результат проверки",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_valid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_expired': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_expiring_soon': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'days_until_expiry': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'warnings': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(type=openapi.TYPE_STRING)  # ✅ ДОБАВЛЕНО
                    ),
                }
            )
        )
    }
)
    @action(detail=True, methods=['get'])
    def verify(self, request, pk=None):
        """Проверить валидность документа"""
        document = self.get_object()
        
        warnings = []
        
        # Проверка срока действия
        if document.is_expired:
            warnings.append("Срок действия документа истёк")
        elif document.is_expiring_soon:
            warnings.append(f"Срок действия истекает через {document.days_until_expiry} дней")
        
        # Проверка наличия обязательных данных
        if not document.file and not document.url:
            warnings.append("Отсутствует скан документа")
        
        if not document.issued_date:
            warnings.append("Не указана дата выдачи")
        
        if not document.expiry_date:
            warnings.append("Не указан срок действия")
        
        is_valid = not document.is_expired and len(warnings) == 0
        
        return Response({
            'is_valid': is_valid,
            'is_expired': document.is_expired,
            'is_expiring_soon': document.is_expiring_soon,
            'days_until_expiry': document.days_until_expiry,
            'warnings': warnings,
            'document': DocumentDetailSerializer(document).data
        })