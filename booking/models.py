# booking/models.py
from django.db import models
from workers.models import Worker
from documentation.models import Nationality, Document
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from ameneties.models import Goods, Services


class Agent(models.Model):
    full_title = models.CharField(
        verbose_name="Полное название компании",
        max_length=100,
        unique=True
    )   
    short_title = models.CharField(
        verbose_name="Краткое наименование",
        max_length=100,  # ✅ ДОБАВЛЕНО (пункт 1)
        unique=True
    )
    IIN_BIN = models.CharField(
        verbose_name="IIN | BIN",
        max_length=100
    )
    adress = models.TextField(
        verbose_name="Юридический адрес",
        max_length=1000
    )
    IBAN = models.CharField(
        verbose_name="IBAN",
        max_length=34
    )
    BIC = models.CharField(
        verbose_name="Идентификатор Банка",
        max_length=100
    )
    
    phone = models.CharField(
        verbose_name="Телефон",
        max_length=20,
        db_index=True
    )
    
    is_active = models.BooleanField(  # ✅ ДОБАВЛЕНО (пункт 3)
        verbose_name="Активен",
        default=True
    )
    
    created_at = models.DateTimeField(  # ✅ ДОБАВЛЕНО (пункт 2)
        verbose_name="Дата создания",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(  # ✅ ДОБАВЛЕНО (пункт 2)
        verbose_name="Дата обновления",
        auto_now=True
    )

    class Meta:
        ordering = ["id"]
        verbose_name = 'Контрагент'
        verbose_name_plural = "Контрагенты"

    def __str__(self):
        return f"{self.full_title}"


class Guest(models.Model):
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message='Введите корректный номер телефона'
    )
    
    first_name = models.CharField(
        verbose_name="Имя",
        max_length=100
    )
    
    last_name = models.CharField(
        verbose_name="Фамилия",
        max_length=100
    )
    
    middle_name = models.CharField(
        verbose_name="Отчество",
        max_length=100,
        blank=True,
        null=True
    )
    
    nationality = models.ForeignKey(
        to=Nationality,
        on_delete=models.PROTECT,
        verbose_name="Гражданство",
        related_name="guests"
    )
    
    documents = models.ManyToManyField(
        to=Document,
        verbose_name="Документы",
        related_name="guests",
        blank=True
    )
    
    phone = models.CharField(
        verbose_name="Телефон",
        max_length=20,
        validators=[phone_validator],
        db_index=True,
        unique=False
    )
    
    email = models.EmailField(
        verbose_name="Email",
        blank=True,
        null=True,
        unique=False
    )
    
    date_of_birth = models.DateField(
        verbose_name="Дата рождения",
        blank=True,
        null=True
    )
    
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    ]
    
    gender = models.CharField(
        verbose_name="Пол",
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    
    blacklisted = models.BooleanField(
        verbose_name="В чёрном списке",
        default=False,
        help_text="Отметьте, если гость в чёрном списке"
    )
    
    blacklist_reason = models.TextField(
        verbose_name="Причина блокировки",
        blank=True,
        null=True
    )
    
    notes = models.TextField(
        verbose_name="Примечания",
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(
        verbose_name="Дата регистрации",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        verbose_name="Дата обновления",
        auto_now=True
    )
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Гость"
        verbose_name_plural = "Гости"
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        """Возвращает полное ФИО"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
    
    @property
    def age(self):
        """Вычисляет возраст гостя"""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    def can_book(self):
        """Проверяет, может ли гость забронировать номер"""
        if self.blacklisted:
            return False, self.blacklist_reason or "Гость в чёрном списке"
        return True, "OK"


class RoomType(models.Model):
    title = models.CharField(
        verbose_name="Тип номера",
        max_length=200
    )
    price = models.DecimalField(
        verbose_name="Цена",
        max_digits=10,
        decimal_places=2,
        help_text="Цена в тенге"
    )
    relevant_from = models.DateField(
        verbose_name="Релевантен с",
        null=True,
        blank=True
    )
    relevant_to = models.DateField(
        verbose_name="Релевантен до",
        null=True,
        blank=True
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
        null=True
    )
    
    is_active = models.BooleanField(
        verbose_name="Активен",
        default=True
    )
    
    created_at = models.DateTimeField(  # ✅ ТОЛЬКО auto_now_add
        verbose_name="Дата создания",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(  # ✅ ТОЛЬКО auto_now
        verbose_name="Дата обновления",
        auto_now=True
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "Тип номера"
        verbose_name_plural = "Типы номеров"
        
    def __str__(self):
        return f"{self.title} - {self.price} ₸"  # ✅ УПРОЩЕНО
    
    @property
    def is_relevant(self):  # ✅ ИСПРАВЛЕНО
        """Проверяет актуальность тарифа"""
        if not self.relevant_from or not self.relevant_to:
            return True
        today = timezone.now().date()
        return self.relevant_from <= today <= self.relevant_to


class Room(models.Model):
    room = models.IntegerField(
        verbose_name="Номер комнаты",
        unique=True,
        db_index=True
    )
    room_types = models.ManyToManyField(
        to=RoomType,
        verbose_name="Доступные тарифы",
        related_name="rooms",
        help_text="Выберите все доступные тарифы для этого номера"
    )
    floor = models.IntegerField(
        verbose_name="Этаж",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        default=True
    )

    class Meta:
        ordering = ["room"]
        verbose_name = "Номер"
        verbose_name_plural = "Номера"

    def __str__(self):
        tariffs_count = self.room_types.count()
        return f"№{self.room} ({tariffs_count} тариф(ов))"
    
    def get_tariffs_display(self):
        """Возвращает строку со всеми тарифами"""
        return ", ".join([rt.title for rt in self.room_types.all()])
    
    def get_current_condition(self):
        """Возвращает текущее состояние номера"""
        return self.reports.filter(condition_end__isnull=True).first()


class RoomCondition(models.Model):
    condition = models.CharField(
        verbose_name="Состояние",
        max_length=100,
        unique=True
    )
    color = models.CharField(
        verbose_name="Цвет",
        max_length=7,
        default="#808080",
        help_text="HEX цвет (#RRGGBB)"
    )
    is_available = models.BooleanField(
        verbose_name="Доступен для бронирования",
        default=False
    )
    
    class Meta:
        ordering = ["id"]
        verbose_name = "Состояние"
        verbose_name_plural = "Состояния"

    def __str__(self):
        return self.condition


class Booking(models.Model):  # ✅ ПЕРЕИМЕНОВАНО (пункт 1)
    """Бронирование"""
    
    class Status(models.IntegerChoices):  # ✅ ИЗМЕНЕНО (пункт 3)
        BOOKED = 1, "Забронирован"
        CHECKED_IN = 2, "Заселён"
        CHECKED_OUT = 3, "Выселен"
        CANCELLED = 4, "Отмена"
    
    agent = models.ForeignKey(
        to=Agent,
        verbose_name="Контрагент",
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True
    )
    guest = models.ForeignKey(
        to=Guest,
        verbose_name="Гость",
        related_name="bookings",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    room = models.ForeignKey(
        to=Room,
        verbose_name="Номер",
        related_name="bookings",
        on_delete=models.PROTECT,
        null=True,  # ✅ ДОБАВЬТЕ
        blank=True  # ✅ ДОБАВЬТЕ
    )
    room_condition = models.ForeignKey(
        to=RoomCondition,
        on_delete=models.PROTECT,
        related_name="bookings",
        verbose_name="Состояние номера",
        null=True,  # ✅ ДОБАВЬТЕ
        blank=True  # ✅ ДОБАВЬТЕ
    )
    status = models.IntegerField(  # ✅ ИЗМЕНЕНО (пункт 2)
        verbose_name="Статус",
        choices=Status.choices,
        default=Status.BOOKED
    )
    
    created_by = models.ForeignKey(  # ✅ ПЕРЕИМЕНОВАНО (пункт 4)
        to=Worker,
        on_delete=models.PROTECT,
        verbose_name="Создал",
        related_name="created_bookings"
    )
    
    check_in = models.DateTimeField(  # ✅ ДОБАВЛЕНО (пункт 5)
        verbose_name="Дата заезда",
        null=True,  # ✅ ДОБАВЬТЕ
        blank=True  # ✅ ДОБАВЬТЕ
    )
    
    check_out = models.DateTimeField(  # ✅ ДОБАВЛЕНО (пункт 5)
        verbose_name="Дата выезда",
        null=True,  # ✅ ДОБАВЬТЕ
        blank=True  # ✅ ДОБАВЬТЕ
    )
    
    note = models.TextField(
        verbose_name="Комментарий",
        max_length=1000,
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(  # ✅ ДОБАВЛЕНО (пункт 6)
        verbose_name="Дата создания",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(  # ✅ ДОБАВЛЕНО (пункт 6)
        verbose_name="Дата обновления",
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self):
        return f"Бронь #{self.id} - Номер {self.room.room} - {self.get_status_display()}"
    
    @property  # ✅ ДОБАВЛЕНО (пункт 7)
    def duration(self):
        """Вычисляет длительность проживания"""
        if self.check_in and self.check_out:
            return self.check_out - self.check_in
        return None


# booking/models.py

class BookingCard(models.Model):
    """Карточка бронирования"""
    
    class Status(models.IntegerChoices):
        ACTIVE = 1, "Активна"
        COMPLETED = 2, "Завершена"
        CANCELLED = 3, "Отменена"
    
    primary_guest = models.ForeignKey(
        to=Guest,
        verbose_name="Основной гость",
        on_delete=models.PROTECT,
        related_name="primary_booking_cards"
    )
    
    bookings = models.ManyToManyField(
        to=Booking,
        verbose_name="Бронирования",
        related_name="booking_cards"
    )
    goods = models.ManyToManyField(
        to=Goods,
        verbose_name="Товары приобретённые",
        blank=True
    )
    services = models.ManyToManyField(
        to=Services,
        verbose_name="Услуги приобретены",
        blank=True
    )
    
    status = models.IntegerField(
        verbose_name="Статус",
        choices=Status.choices,
        default=Status.ACTIVE
    )
    
    total_amount = models.DecimalField(
        verbose_name="Общая сумма",
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        verbose_name="Дата обновления",
        auto_now=True
    )
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Карточка бронирования"
        verbose_name_plural = "Карточки бронирования"
    
    def __str__(self):
        return f"Карточка #{self.id} - {self.primary_guest.full_name}"
    
    @property
    def total_bookings(self):
        """Количество бронирований"""
        return self.bookings.count()
    
    @property
    def total_goods_amount(self):
        """Общая сумма товаров"""
        return sum(g.price for g in self.goods.all())
    
    @property
    def total_services_amount(self):
        """Общая сумма услуг"""
        return sum(s.price for s in self.services.all())
    
    def calculate_total(self): 
        """Пересчитать общую сумму на основе бронирований, товаров и услуг"""
        bookings_total = 0
        
        # Считаем стоимость всех бронирований
        for booking in self.bookings.all():
            if booking.room and booking.room.room_types.exists():
                # Берём первый тариф из доступных
                room_type = booking.room.room_types.first()
                
                # Если есть даты заезда и выезда, умножаем на количество дней
                if booking.check_in and booking.check_out:
                    days = (booking.check_out - booking.check_in).days
                    if days > 0:
                        bookings_total += room_type.price * days
                    else:
                        # Минимум 1 день
                        bookings_total += room_type.price
                else:
                    # Если дат нет, считаем как 1 день
                    bookings_total += room_type.price
        
        # Добавляем товары и услуги
        goods_total = self.total_goods_amount
        services_total = self.total_services_amount
        
        # Обновляем общую сумму
        self.total_amount = bookings_total + goods_total + services_total
        self.save()
        
        return self.total_amount