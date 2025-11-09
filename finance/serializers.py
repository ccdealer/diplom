# payments/serializers.py
from rest_framework import serializers
from .models import CardPayment, CashPayment, BankPayment, PaymentOrder
from django.utils import timezone


# ==================== Card Payment Serializers ====================

class CardPaymentListSerializer(serializers.ModelSerializer):
    """Список оплат картой"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    booking_card_number = serializers.IntegerField(source='booking_card.id', read_only=True)
    
    class Meta:
        model = CardPayment
        fields = [
            'id', 'amount', 'agent', 'agent_name',
            'booking_card', 'booking_card_number', 'is_chargeback',
            'cheque_id', 'issue_date'
        ]
        read_only_fields = ['id']


class CardPaymentDetailSerializer(serializers.ModelSerializer):
    """Детали оплаты картой"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    
    class Meta:
        model = CardPayment
        fields = '__all__'
        read_only_fields = ['id']


class CardPaymentCreateSerializer(serializers.ModelSerializer):
    """Создание оплаты картой"""
    
    class Meta:
        model = CardPayment
        fields = [
            'amount', 'agent', 'booking_card', 'is_chargeback',
            'cheque_id', 'issue_date'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля")
        return value
    
    def validate_issue_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Дата оплаты не может быть в будущем")
        return value


# ==================== Cash Payment Serializers ====================

class CashPaymentListSerializer(serializers.ModelSerializer):
    """Список наличных оплат"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    booking_card_number = serializers.IntegerField(source='booking_card.id', read_only=True)
    received_by_name = serializers.CharField(source='received_by.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CashPayment
        fields = [
            'id', 'amount', 'agent', 'agent_name',
            'booking_card', 'booking_card_number', 'is_chargeback',
            'cheque_id', 'received_by', 'received_by_name', 'issue_date'
        ]
        read_only_fields = ['id', 'issue_date']


class CashPaymentDetailSerializer(serializers.ModelSerializer):
    """Детали наличной оплаты"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    received_by_name = serializers.CharField(source='received_by.name', read_only=True, allow_null=True)
    
    class Meta:
        model = CashPayment
        fields = '__all__'
        read_only_fields = ['id', 'issue_date']


class CashPaymentCreateSerializer(serializers.ModelSerializer):
    """Создание наличной оплаты"""
    
    class Meta:
        model = CashPayment
        fields = [
            'amount', 'agent', 'booking_card', 'is_chargeback',
            'cheque_id', 'received_by'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля")
        return value


# ==================== Bank Payment Serializers ====================

class BankPaymentListSerializer(serializers.ModelSerializer):
    """Список банковских переводов"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    booking_card_number = serializers.IntegerField(source='booking_card.id', read_only=True)
    
    class Meta:
        model = BankPayment
        fields = [
            'id', 'amount', 'agent', 'agent_name',
            'booking_card', 'booking_card_number', 'is_chargeback',
            'reference_number', 'bank_name', 'issue_date'
        ]
        read_only_fields = ['id']


class BankPaymentDetailSerializer(serializers.ModelSerializer):
    """Детали банковского перевода"""
    agent_name = serializers.CharField(source='agent.name', read_only=True)
    
    class Meta:
        model = BankPayment
        fields = '__all__'
        read_only_fields = ['id']


class BankPaymentCreateSerializer(serializers.ModelSerializer):
    """Создание банковского перевода"""
    
    class Meta:
        model = BankPayment
        fields = [
            'amount', 'agent', 'booking_card', 'is_chargeback',
            'reference_number', 'bank_name', 'issue_date'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма должна быть больше нуля")
        return value
    
    def validate_issue_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Дата оплаты не может быть в будущем")
        return value


# ==================== Payment Order Serializers ====================

class PaymentOrderSerializer(serializers.ModelSerializer):
    """Сериализатор платёжного ордера"""
    card_payments = CardPaymentListSerializer(many=True, read_only=True)
    cash_payments = CashPaymentListSerializer(many=True, read_only=True)
    bank_payments = BankPaymentListSerializer(many=True, read_only=True)
    
    total_card = serializers.SerializerMethodField(read_only=True)
    total_cash = serializers.SerializerMethodField(read_only=True)
    total_bank = serializers.SerializerMethodField(read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    payment_breakdown = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = PaymentOrder
        fields = [
            'id', 'booking_card', 'card_payments', 'cash_payments',
            'bank_payments', 'total_card', 'total_cash', 'total_bank',
            'total_amount', 'payment_breakdown', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_total_card(self, obj):
        return float(obj.total_card)
    
    def get_total_cash(self, obj):
        return float(obj.total_cash)
    
    def get_total_bank(self, obj):
        return float(obj.total_bank)
    
    def get_total_amount(self, obj):
        return float(obj.total_amount)
    
    def get_payment_breakdown(self, obj):
        return obj.payment_breakdown


class PaymentOrderCreateSerializer(serializers.ModelSerializer):
    """Создание платёжного ордера"""
    
    class Meta:
        model = PaymentOrder
        fields = ['booking_card', 'notes']
    
    def validate_booking_card(self, value):
        """Проверка, что для бронирования ещё нет ордера"""
        if PaymentOrder.objects.filter(booking_card=value).exists():
            raise serializers.ValidationError(
                "Для этого бронирования уже существует платёжный ордер"
            )
        return value