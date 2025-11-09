from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


class Nationality(models.Model):
    nationality = models.CharField(
        verbose_name="Национальность",
        max_length=100,  
        unique=True 
    )
    code = models.CharField(  
        verbose_name="Код страны",
        max_length=3,
        blank=True,
        null=True,
        help_text="ISO код страны"
    )

    class Meta:
        ordering = ["nationality"]  
        verbose_name = "Национальность"
        verbose_name_plural = "Национальности"

    def __str__(self):
        return self.nationality


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('passport', 'Паспорт'),
        ('id_card', 'Удостоверение личности')
    ]
    
    # Валидатор для ИИН
    iin_validator = RegexValidator(
        regex=r'^\d{12}$',
        message='ИИН должен содержать ровно 12 цифр'
    )

    nationality = models.ForeignKey(
        to=Nationality,
        on_delete=models.PROTECT,
        verbose_name="Гражданство",  
        related_name="documents"  
    )
    
    IIN = models.CharField(
        verbose_name="ИИН",
        max_length=12,
        validators=[iin_validator],  
        unique=True, 
        db_index=True,  
        help_text="12 цифр без пробелов"
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
    
    date_of_birth = models.DateField( 
        verbose_name="Дата рождения",
        blank=True,
        null=True
    )

    document_type = models.CharField(
        verbose_name="Тип документа",
        max_length=50,
        choices=DOCUMENT_TYPES,
        default='passport' 
    )
    
    number = models.CharField(
        verbose_name="Номер документа",
        max_length=100,
        db_index=True 
    )
    
    file = models.FileField(
        verbose_name="Скан документа",
        upload_to='documents/%Y/%m/',
        blank=True,
        null=True,
        help_text="Загрузите скан или фото документа"
    )
    
    url = models.URLField(
        verbose_name="Ссылка на документ",
        max_length=1000,
        blank=True,
        null=True,
        help_text="Внешняя ссылка на документ (если файл хранится в облаке)"
    )
    
    issued_date = models.DateField(
        verbose_name="Дата выдачи",
        blank=True,
        null=True
    )
    
    expiry_date = models.DateField(
        verbose_name="Срок действия до",
        blank=True,
        null=True
    )
    
    issued_by = models.CharField(
        verbose_name="Кем выдан",
        max_length=500,
        blank=True,
        null=True
    )
    
    uploaded_at = models.DateTimeField(
        verbose_name="Дата загрузки",
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(  
        verbose_name="Дата обновления",
        auto_now=True
    )
    
    notes = models.TextField(
        verbose_name="Примечания",
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Документ гостя"
        verbose_name_plural = "Документы гостей"
        indexes = [
            models.Index(fields=['IIN', 'document_type']),
            models.Index(fields=['number', 'document_type']),
        ]

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name}"
        return f"{self.get_document_type_display()} - {full_name} ({self.number or 'б/н'})"
    
    @property
    def full_name(self): 
        """Возвращает полное ФИО"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)
    
    @property
    def is_expired(self):
        """Проверяет, истёк ли срок действия документа"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False
    
    @property
    def days_until_expiry(self): 
        """Сколько дней до истечения срока действия"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None
    
    @property
    def is_expiring_soon(self): 
        """Проверяет, истекает ли документ в ближайшие 30 дней"""
        days = self.days_until_expiry
        if days is not None:
            return 0 < days <= 30
        return False
    
    def clean(self):  
        """Проверка корректности данных"""
        super().clean()
        
        if self.issued_date and self.expiry_date:
            if self.issued_date >= self.expiry_date:
                raise ValidationError({
                    'expiry_date': 'Срок действия должен быть позже даты выдачи'
                })
        
        if self.date_of_birth and self.issued_date:
            if self.date_of_birth >= self.issued_date:
                raise ValidationError({
                    'issued_date': 'Дата выдачи должна быть позже даты рождения'
                })
        
        if self.IIN and self.date_of_birth:
            try:
                year = int(self.IIN[0:2])
                month = int(self.IIN[2:4])
                day = int(self.IIN[4:6])
                
                century_digit = int(self.IIN[6])
                if century_digit in [3, 4]:
                    year += 1900
                elif century_digit in [5, 6]:
                    year += 2000
                
                from datetime import date
                iin_date = date(year, month, day)
                
                if iin_date != self.date_of_birth:
                    raise ValidationError({
                        'IIN': f'ИИН не соответствует дате рождения. По ИИН: {iin_date}'
                    })
            except (ValueError, IndexError):
                pass  