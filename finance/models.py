from django.db import models
from django.utils import timezone
from booking.models import Agent, BookingCard


class CardPayment(models.Model):
    """Оплата картой"""
    
    amount = models.DecimalField(
        verbose_name="Сумма",
        max_digits=10,
        decimal_places=2
    )
    
    agent = models.ForeignKey(
        to=Agent,
        on_delete=models.PROTECT,
        related_name="card_payments",
        verbose_name="Контрагент"
    )
    
    booking_card = models.ForeignKey(
        to=BookingCard,
        verbose_name="Карточка бронирования",
        on_delete=models.PROTECT,
        related_name="card_payments"
    )
    
    is_chargeback = models.BooleanField(
        verbose_name="Возврат",
        default=False
    )
    
    cheque_id = models.CharField(
        verbose_name="ID Чека",
        max_length=100,
        blank=True,
        null=True
    )
    
    issue_date = models.DateTimeField(
        verbose_name="Дата оплаты",
        default=timezone.now  # ✅ ИЗМЕНЕНО (CardPayment пункт 3)
    )
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Оплата картой"
        verbose_name_plural = "Оплаты картой"
    
    def __str__(self):
        return f"Карта: {self.amount} ₸ - {self.issue_date.strftime('%d.%m.%Y')}"


class CashPayment(models.Model):
    """Оплата наличными"""
    
    amount = models.DecimalField(
        verbose_name="Сумма",
        max_digits=10,
        decimal_places=2
    )
    
    agent = models.ForeignKey(
        to=Agent,
        on_delete=models.PROTECT,
        related_name="cash_payments",
        verbose_name="Контрагент"
    )
    
    booking_card = models.ForeignKey(
        to=BookingCard,
        verbose_name="Карточка бронирования",
        on_delete=models.PROTECT,
        related_name="cash_payments"
    )
    
    is_chargeback = models.BooleanField(
        verbose_name="Возврат",
        default=False
    )

    cheque_id = models.CharField(
        verbose_name="ID Чека",
        max_length=100,
        blank=True,
        null=True
    )
    
    received_by = models.ForeignKey(
        to='workers.Worker',
        verbose_name="Принял",
        on_delete=models.PROTECT,
        related_name="received_cash_payments",
        blank=True,
        null=True
    )
    
    issue_date = models.DateTimeField(
        verbose_name="Дата оплаты",
        auto_now_add=True
    )
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Оплата наличными"
        verbose_name_plural = "Оплаты наличными"
    
    def __str__(self):
        return f"Наличные: {self.amount} ₸ - {self.issue_date.strftime('%d.%m.%Y')}"


class BankPayment(models.Model):
    """Банковский перевод"""
    
    amount = models.DecimalField(
        verbose_name="Сумма",
        max_digits=10,
        decimal_places=2
    )
    
    agent = models.ForeignKey(
        to=Agent,
        on_delete=models.PROTECT,
        related_name="bank_payments",
        verbose_name="Контрагент"
    )
    
    booking_card = models.ForeignKey(
        to=BookingCard,
        verbose_name="Карточка бронирования",
        on_delete=models.PROTECT,
        related_name="bank_payments"
    )
    
    is_chargeback = models.BooleanField(
        verbose_name="Возврат",
        default=False
    )
    
    reference_number = models.CharField(
        verbose_name="Номер платёжного поручения",
        max_length=50,
        blank=True,
        null=True
    )
    
    bank_name = models.CharField(
        verbose_name="Название банка",
        max_length=200,
        blank=True,
        null=True
    )
    
    issue_date = models.DateTimeField(
        verbose_name="Дата оплаты",
        default=timezone.now  # ✅ ИЗМЕНЕНО (BankPayment пункт 3)
    )
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = "Банковский перевод"
        verbose_name_plural = "Банковские переводы"
    
    def __str__(self):
        return f"Банк: {self.amount} ₸ - {self.issue_date.strftime('%d.%m.%Y')}"


class PaymentOrder(models.Model):
    """Платёжный ордер (сводка всех платежей по бронированию)"""
    
    booking_card = models.OneToOneField(
        to=BookingCard,
        verbose_name="Карточка бронирования",
        on_delete=models.PROTECT,
        related_name="payment_order"
    )
    
    card_payments = models.ManyToManyField(
        to=CardPayment,
        verbose_name="Оплаты картой",
        blank=True,
        related_name="payment_orders"
    )
    
    cash_payments = models.ManyToManyField(
        to=CashPayment,
        verbose_name="Оплаты наличными",
        blank=True,
        related_name="payment_orders"
    )
    
    bank_payments = models.ManyToManyField(
        to=BankPayment,
        verbose_name="Банковские переводы",
        blank=True,
        related_name="payment_orders"
    )
    
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True
    )
    
    notes = models.TextField(
        verbose_name="Примечания",
        blank=True,
        null=True
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Платёжный ордер"
        verbose_name_plural = "Платёжные ордера"
    
    def __str__(self):
        return f"Ордер для {self.booking_card}"
    
    @property
    def total_card(self):
        """Общая сумма по картам"""
        total = sum(
            p.amount if not p.is_chargeback else -p.amount
            for p in self.card_payments.all()
        )
        return total
    
    @property
    def total_cash(self):
        """Общая сумма наличными"""
        total = sum(
            p.amount if not p.is_chargeback else -p.amount
            for p in self.cash_payments.all()
        )
        return total
    
    @property
    def total_bank(self):
        """Общая сумма банковских переводов"""
        total = sum(
            p.amount if not p.is_chargeback else -p.amount
            for p in self.bank_payments.all()
        )
        return total
    
    @property
    def total_amount(self):
        """Общая сумма всех платежей"""
        return self.total_card + self.total_cash + self.total_bank
    
    @property
    def payment_breakdown(self):
        """Детализация платежей"""
        return {  # ✅ ИЗМЕНЕНО (PaymentOrder пункт 2)
            'card': float(self.total_card),
            'cash': float(self.total_cash),
            'bank': float(self.total_bank),
            'total': float(self.total_amount)
        }