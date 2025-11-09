# payments/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CardPaymentViewSet,
    CashPaymentViewSet,
    BankPaymentViewSet,
    PaymentOrderViewSet
)

app_name = 'payments'

router = DefaultRouter()
router.register(r'card-payments', CardPaymentViewSet, basename='cardpayment')
router.register(r'cash-payments', CashPaymentViewSet, basename='cashpayment')
router.register(r'bank-payments', BankPaymentViewSet, basename='bankpayment')
router.register(r'payment-orders', PaymentOrderViewSet, basename='paymentorder')

urlpatterns = [
    path('', include(router.urls)),
]