# payments/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone

from .models import CardPayment, CashPayment, BankPayment, PaymentOrder
from .serializers import (
    CardPaymentListSerializer, CardPaymentDetailSerializer, CardPaymentCreateSerializer,
    CashPaymentListSerializer, CashPaymentDetailSerializer, CashPaymentCreateSerializer,
    BankPaymentListSerializer, BankPaymentDetailSerializer, BankPaymentCreateSerializer,
    PaymentOrderSerializer, PaymentOrderCreateSerializer
)


class CardPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для оплат картой
    
    list: Список всех оплат картой
    retrieve: Детали конкретной оплаты
    create: Создать новую оплату
    update: Обновить оплату
    partial_update: Частично обновить оплату
    destroy: Удалить оплату
    """
    queryset = CardPayment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['agent', 'booking_card', 'is_chargeback']
    search_fields = ['cheque_id', 'agent__name']
    ordering_fields = ['issue_date', 'amount']
    ordering = ['-issue_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CardPaymentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CardPaymentCreateSerializer
        return CardPaymentDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список оплат картой",
        operation_description="Получить все оплаты картой с фильтрацией"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать оплату картой",
        operation_description="Создать новую оплату картой"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Статистика оплат картой",
        operation_description="Общая статистика по оплатам картой",
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика оплат картой"""
        queryset = self.get_queryset()
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(issue_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(issue_date__lte=date_to)
        
        payments = queryset.filter(is_chargeback=False)
        chargebacks = queryset.filter(is_chargeback=True)
        
        total_payments = sum(p.amount for p in payments)
        total_chargebacks = sum(p.amount for p in chargebacks)
        net_amount = total_payments - total_chargebacks
        
        return Response({
            'total_payments_count': payments.count(),
            'total_chargebacks_count': chargebacks.count(),
            'total_payments_amount': float(total_payments),
            'total_chargebacks_amount': float(total_chargebacks),
            'net_amount': float(net_amount)
        })


class CashPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для наличных оплат
    """
    queryset = CashPayment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['agent', 'booking_card', 'is_chargeback', 'received_by']
    search_fields = ['cheque_id', 'agent__name', 'received_by__name']
    ordering_fields = ['issue_date', 'amount']
    ordering = ['-issue_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CashPaymentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CashPaymentCreateSerializer
        return CashPaymentDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список наличных оплат",
        operation_description="Получить все наличные оплаты с фильтрацией"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать наличную оплату",
        operation_description="Создать новую наличную оплату"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Статистика наличных оплат",
        operation_description="Общая статистика по наличным оплатам"
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика наличных оплат"""
        queryset = self.get_queryset()
        
        payments = queryset.filter(is_chargeback=False)
        chargebacks = queryset.filter(is_chargeback=True)
        
        total_payments = sum(p.amount for p in payments)
        total_chargebacks = sum(p.amount for p in chargebacks)
        net_amount = total_payments - total_chargebacks
        
        # По сотрудникам
        by_worker = {}
        for payment in queryset.filter(received_by__isnull=False):
            worker_name = payment.received_by.name
            if worker_name not in by_worker:
                by_worker[worker_name] = {'count': 0, 'total': 0}
            
            amount = payment.amount if not payment.is_chargeback else -payment.amount
            by_worker[worker_name]['count'] += 1
            by_worker[worker_name]['total'] += float(amount)
        
        return Response({
            'total_payments_count': payments.count(),
            'total_chargebacks_count': chargebacks.count(),
            'total_payments_amount': float(total_payments),
            'total_chargebacks_amount': float(total_chargebacks),
            'net_amount': float(net_amount),
            'by_worker': by_worker
        })


class BankPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для банковских переводов
    """
    queryset = BankPayment.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['agent', 'booking_card', 'is_chargeback', 'bank_name']
    search_fields = ['reference_number', 'bank_name', 'agent__name']
    ordering_fields = ['issue_date', 'amount']
    ordering = ['-issue_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BankPaymentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BankPaymentCreateSerializer
        return BankPaymentDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список банковских переводов",
        operation_description="Получить все банковские переводы с фильтрацией"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать банковский перевод",
        operation_description="Создать новый банковский перевод"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Статистика банковских переводов",
        operation_description="Общая статистика по банковским переводам"
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Статистика банковских переводов"""
        queryset = self.get_queryset()
        
        payments = queryset.filter(is_chargeback=False)
        chargebacks = queryset.filter(is_chargeback=True)
        
        total_payments = sum(p.amount for p in payments)
        total_chargebacks = sum(p.amount for p in chargebacks)
        net_amount = total_payments - total_chargebacks
        
        # По банкам
        by_bank = {}
        for payment in queryset.filter(bank_name__isnull=False):
            bank_name = payment.bank_name
            if bank_name not in by_bank:
                by_bank[bank_name] = {'count': 0, 'total': 0}
            
            amount = payment.amount if not payment.is_chargeback else -payment.amount
            by_bank[bank_name]['count'] += 1
            by_bank[bank_name]['total'] += float(amount)
        
        return Response({
            'total_payments_count': payments.count(),
            'total_chargebacks_count': chargebacks.count(),
            'total_payments_amount': float(total_payments),
            'total_chargebacks_amount': float(total_chargebacks),
            'net_amount': float(net_amount),
            'by_bank': by_bank
        })


class PaymentOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet для платёжных ордеров
    """
    queryset = PaymentOrder.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentOrderCreateSerializer
        return PaymentOrderSerializer
    
    @swagger_auto_schema(
        operation_summary="Список платёжных ордеров",
        operation_description="Получить все платёжные ордера"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать платёжный ордер",
        operation_description="Создать новый платёжный ордер для бронирования"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Добавить оплату картой",
        operation_description="Добавить существующую оплату картой к ордеру",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['payment_id'],
            properties={
                'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID оплаты")
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_card_payment(self, request, pk=None):
        """Добавить оплату картой к ордеру"""
        order = self.get_object()
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response(
                {'error': 'Укажите payment_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = CardPayment.objects.get(id=payment_id)
            order.card_payments.add(payment)
            serializer = PaymentOrderSerializer(order)
            return Response(serializer.data)
        except CardPayment.DoesNotExist:
            return Response(
                {'error': 'Оплата не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_summary="Добавить наличную оплату",
        operation_description="Добавить существующую наличную оплату к ордеру",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['payment_id'],
            properties={
                'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID оплаты")
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_cash_payment(self, request, pk=None):
        """Добавить наличную оплату к ордеру"""
        order = self.get_object()
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response(
                {'error': 'Укажите payment_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = CashPayment.objects.get(id=payment_id)
            order.cash_payments.add(payment)
            serializer = PaymentOrderSerializer(order)
            return Response(serializer.data)
        except CashPayment.DoesNotExist:
            return Response(
                {'error': 'Оплата не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @swagger_auto_schema(
        operation_summary="Добавить банковский перевод",
        operation_description="Добавить существующий банковский перевод к ордеру",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['payment_id'],
            properties={
                'payment_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID перевода")
            }
        )
    )
    @action(detail=True, methods=['post'])
    def add_bank_payment(self, request, pk=None):
        """Добавить банковский перевод к ордеру"""
        order = self.get_object()
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response(
                {'error': 'Укажите payment_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment = BankPayment.objects.get(id=payment_id)
            order.bank_payments.add(payment)
            serializer = PaymentOrderSerializer(order)
            return Response(serializer.data)
        except BankPayment.DoesNotExist:
            return Response(
                {'error': 'Перевод не найден'},
                status=status.HTTP_404_NOT_FOUND
            )