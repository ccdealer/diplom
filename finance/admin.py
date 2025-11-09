# payments/admin.py
from django.contrib import admin
from .models import CardPayment, CashPayment, BankPayment, PaymentOrder


@admin.register(CardPayment)
class CardPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'agent', 'booking_card', 'is_chargeback', 'cheque_id', 'issue_date']
    list_filter = ['is_chargeback', 'issue_date']
    search_fields = ['cheque_id', 'agent__name']
    date_hierarchy = 'issue_date'


@admin.register(CashPayment)
class CashPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'agent', 'booking_card', 'is_chargeback', 'received_by', 'issue_date']
    list_filter = ['is_chargeback', 'received_by', 'issue_date']
    search_fields = ['cheque_id', 'agent__name', 'received_by__name']
    date_hierarchy = 'issue_date'


@admin.register(BankPayment)
class BankPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'amount', 'agent', 'booking_card', 'is_chargeback', 'bank_name', 'reference_number', 'issue_date']
    list_filter = ['is_chargeback', 'bank_name', 'issue_date']
    search_fields = ['reference_number', 'bank_name', 'agent__name']
    date_hierarchy = 'issue_date'


@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking_card', 'get_total_amount', 'created_at']
    filter_horizontal = ['card_payments', 'cash_payments', 'bank_payments']
    readonly_fields = ['created_at']
    
    def get_total_amount(self, obj):
        return f"{obj.total_amount} ₸"
    get_total_amount.short_description = 'Общая сумма'