# booking/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Count, Q

from .models import Agent, Guest, RoomType, Room, RoomCondition, Booking, BookingCard
from .serializers import (
    AgentListSerializer, AgentDetailSerializer, AgentCreateUpdateSerializer,
    GuestListSerializer, GuestDetailSerializer, GuestCreateUpdateSerializer,
    RoomTypeListSerializer, RoomTypeDetailSerializer, RoomTypeCreateUpdateSerializer,
    RoomListSerializer, RoomDetailSerializer, RoomCreateUpdateSerializer,
    RoomConditionSerializer,
    BookingListSerializer, BookingDetailSerializer, BookingCreateUpdateSerializer,
    BookingCardListSerializer, BookingCardDetailSerializer, BookingCardCreateUpdateSerializer
)


class AgentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для контрагентов
    
    list: Список всех контрагентов
    retrieve: Детали контрагента
    create: Создать контрагента
    update: Обновить контрагента
    partial_update: Частично обновить контрагента
    destroy: Удалить контрагента
    """
    queryset = Agent.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['full_title', 'short_title', 'IIN_BIN', 'phone']
    ordering_fields = ['id', 'full_title', 'created_at']
    ordering = ['id']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AgentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AgentCreateUpdateSerializer
        return AgentDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список контрагентов",
        operation_description="Получить все контрагенты с фильтрацией и поиском"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать контрагента",
        operation_description="Создать нового контрагента"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Бронирования контрагента",
        operation_description="Получить все бронирования конкретного контрагента"
    )
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Получить бронирования контрагента"""
        agent = self.get_object()
        bookings = agent.bookings.all()
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)


class GuestViewSet(viewsets.ModelViewSet):
    """
    ViewSet для гостей
    """
    queryset = Guest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['nationality', 'gender', 'blacklisted']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email']
    ordering_fields = ['id', 'last_name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return GuestListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GuestCreateUpdateSerializer
        return GuestDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список гостей",
        operation_description="Получить всех гостей с фильтрацией и поиском"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать гостя",
        operation_description="Создать нового гостя"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Гости в чёрном списке",
        operation_description="Получить всех гостей в чёрном списке"
    )
    @action(detail=False, methods=['get'])
    def blacklisted(self, request):
        """Гости в чёрном списке"""
        guests = self.get_queryset().filter(blacklisted=True)
        serializer = GuestListSerializer(guests, many=True)
        return Response({
            'count': guests.count(),
            'guests': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Бронирования гостя",
        operation_description="Получить все бронирования конкретного гостя"
    )
    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Получить бронирования гостя"""
        guest = self.get_object()
        bookings = guest.bookings.all()
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Добавить в чёрный список",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['reason'],
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description="Причина блокировки")
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_to_blacklist(self, request, pk=None):
        """Добавить гостя в чёрный список"""
        guest = self.get_object()
        reason = request.data.get('reason')
        
        if not reason:
            return Response(
                {'error': 'Укажите причину блокировки'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        guest.blacklisted = True
        guest.blacklist_reason = reason
        guest.save()
        
        serializer = GuestDetailSerializer(guest)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Удалить из чёрного списка"
    )
    @action(detail=True, methods=['post'])
    def remove_from_blacklist(self, request, pk=None):
        """Удалить гостя из чёрного списка"""
        guest = self.get_object()
        guest.blacklisted = False
        guest.blacklist_reason = None
        guest.save()
        
        serializer = GuestDetailSerializer(guest)
        return Response(serializer.data)


class RoomTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для типов номеров
    """
    queryset = RoomType.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'price', 'created_at']
    ordering = ['title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoomTypeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RoomTypeCreateUpdateSerializer
        return RoomTypeDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список типов номеров",
        operation_description="Получить все типы номеров"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Активные типы номеров",
        operation_description="Получить только активные типы номеров"
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Активные типы номеров"""
        room_types = self.get_queryset().filter(is_active=True)
        serializer = RoomTypeListSerializer(room_types, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Актуальные типы номеров",
        operation_description="Получить типы номеров актуальные на текущую дату"
    )
    @action(detail=False, methods=['get'])
    def relevant(self, request):
        """Актуальные типы номеров"""
        today = timezone.now().date()
        room_types = self.get_queryset().filter(
            Q(relevant_from__isnull=True) | Q(relevant_from__lte=today),
            Q(relevant_to__isnull=True) | Q(relevant_to__gte=today),
            is_active=True
        )
        serializer = RoomTypeListSerializer(room_types, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    """
    ViewSet для номеров
    """
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['floor', 'is_active', 'room_types']
    search_fields = ['room']
    ordering_fields = ['room', 'floor']
    ordering = ['room']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoomListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return RoomCreateUpdateSerializer
        return RoomDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список номеров",
        operation_description="Получить все номера"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Доступные номера",
        operation_description="Получить номера доступные для бронирования"
    )
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Доступные номера"""
        rooms = self.get_queryset().filter(is_active=True)
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data)


class RoomConditionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для состояний номеров
    """
    queryset = RoomCondition.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = RoomConditionSerializer
    
    @swagger_auto_schema(
        operation_summary="Список состояний",
        operation_description="Получить все возможные состояния номеров"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet для бронирований
    """
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'guest', 'agent', 'room', 'created_by']
    search_fields = ['guest__first_name', 'guest__last_name', 'agent__full_title', 'note']
    ordering_fields = ['id', 'check_in', 'check_out', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookingListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookingCreateUpdateSerializer
        return BookingDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список бронирований",
        operation_description="Получить все бронирования"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать бронирование",
        operation_description="Создать новое бронирование"
    )
    def create(self, request, *args, **kwargs):
        """Создать новое бронирование - возвращает полные данные с ID"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # После создания возвращаем полные данные через BookingDetailSerializer
        instance = serializer.instance
        detail_serializer = BookingDetailSerializer(instance)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            detail_serializer.data,  # ✅ Теперь включает id и все read_only поля
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    @swagger_auto_schema(
        operation_summary="Активные бронирования",
        operation_description="Получить активные бронирования (забронированы и заселены)"
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Активные бронирования"""
        bookings = self.get_queryset().filter(
            status__in=[Booking.Status.BOOKED, Booking.Status.CHECKED_IN]
        )
        serializer = BookingListSerializer(bookings, many=True)
        return Response({
            'count': bookings.count(),
            'bookings': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Заселить",
        operation_description="Изменить статус на 'Заселён'"
    )
    @action(detail=True, methods=['post'])
    def check_in(self, request, pk=None):
        """Заселить гостя"""
        booking = self.get_object()
        
        if booking.status != Booking.Status.BOOKED:
            return Response(
                {'error': 'Можно заселить только забронированные номера'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.Status.CHECKED_IN
        booking.save()
        
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Выселить",
        operation_description="Изменить статус на 'Выселен'"
    )
    @action(detail=True, methods=['post'])
    def check_out(self, request, pk=None):
        """Выселить гостя"""
        booking = self.get_object()
        
        if booking.status != Booking.Status.CHECKED_IN:
            return Response(
                {'error': 'Можно выселить только заселённых гостей'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.Status.CHECKED_OUT
        booking.save()
        
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Отменить",
        operation_description="Отменить бронирование"
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отменить бронирование"""
        booking = self.get_object()
        
        if booking.status in [Booking.Status.CHECKED_OUT, Booking.Status.CANCELLED]:
            return Response(
                {'error': 'Нельзя отменить завершённое или уже отменённое бронирование'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = Booking.Status.CANCELLED
        booking.save()
        
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)




class BookingCardViewSet(viewsets.ModelViewSet):
    """
    ViewSet для карточек бронирования
    """
    queryset = BookingCard.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'primary_guest']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookingCardListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookingCardCreateUpdateSerializer
        return BookingCardDetailSerializer
    
    def perform_create(self, serializer):
        """Автоматический расчёт при создании"""
        booking_card = serializer.save()
        booking_card.calculate_total()
    
    def perform_update(self, serializer):
        """Автоматический расчёт при обновлении"""
        booking_card = serializer.save()
        booking_card.calculate_total()
    
    @swagger_auto_schema(
        operation_summary="Список карточек",
        operation_description="Получить все карточки бронирования"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать карточку",
        operation_description="Создать новую карточку с автоматическим расчётом суммы"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Обновить карточку",
        operation_description="Обновить карточку с автоматическим пересчётом суммы"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Частично обновить карточку",
        operation_description="Частично обновить карточку с автоматическим пересчётом суммы"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Пересчитать сумму",
        operation_description="Пересчитать общую сумму карточки вручную"
    )
    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Пересчитать общую сумму вручную"""
        card = self.get_object()
        total = card.calculate_total()
        
        detail_serializer = BookingCardDetailSerializer(card)
        return Response({
            'total_amount': float(total),
            'message': 'Сумма пересчитана',
            'card': detail_serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Добавить бронирование",
        operation_description="Добавить бронирование к карточке с пересчётом суммы",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['booking_id'],
            properties={
                'booking_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_booking(self, request, pk=None):
        """Добавить бронирование к карточке"""
        card = self.get_object()
        booking_id = request.data.get('booking_id')
        
        if not booking_id:
            return Response(
                {'error': 'Укажите booking_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            booking = Booking.objects.get(id=booking_id)
            card.bookings.add(booking)
            card.calculate_total()
            
            serializer = BookingCardDetailSerializer(card)
            return Response(serializer.data)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Бронирование не найдено'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_summary="Добавить товар/услугу",
        operation_description="Добавить товары или услуги с пересчётом суммы",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'goods': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER)
                ),
                'services': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER)
                )
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_items(self, request, pk=None):
        """Добавить товары или услуги"""
        card = self.get_object()
        
        goods_ids = request.data.get('goods', [])
        services_ids = request.data.get('services', [])
        
        # Добавляем товары
        if goods_ids:
            for goods_id in goods_ids:
                try:
                    goods = Goods.objects.get(id=goods_id)
                    card.goods.add(goods)
                except Goods.DoesNotExist:
                    pass
        
        # Добавляем услуги
        if services_ids:
            for service_id in services_ids:
                try:
                    service = Services.objects.get(id=service_id)
                    card.services.add(service)
                except Services.DoesNotExist:
                    pass
        
        # Пересчитываем сумму
        card.calculate_total()
        
        serializer = BookingCardDetailSerializer(card)
        return Response(serializer.data)