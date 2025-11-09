from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class JobTitle(models.Model):
    title = models.CharField(
        verbose_name="Должность",
        max_length=100,
        unique=True 
    )
    pay_per_hour = models.IntegerField(
        verbose_name="Оплата за час работы",
        help_text="Указывается в тенге"
    )

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ['title']  

    def __str__(self):
        return f"{self.title} ({self.pay_per_hour} ₸/час)"
    
class Worker(models.Model):
    name = models.CharField(
        verbose_name="ФИО сотрудника",
        max_length=100
    )
    main_occupation = models.ForeignKey(
        to=JobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workers",
        verbose_name="Основная должность"
    )
    telegram_id = models.BigIntegerField(
        verbose_name="Telegram ID",
        unique=True,
        db_index=True
    )
    telegram_username = models.CharField( 
        verbose_name="Telegram username",
        max_length=100,
        blank=True,
        null=True
    )
    is_working = models.BooleanField(
        verbose_name="Работает",
        default=False
    )
    created_at = models.DateTimeField( 
        verbose_name="Дата добавления",
        auto_now_add=True
    )
    user = models.ForeignKey(
        to=User,
        verbose_name="Ссылка на юзера",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = "Сотрудники"
        ordering = ['name']

    def __str__(self):
        status = "работает" if self.is_working else "не работает"
        return f"{self.name} ({status})"
    
class Report(models.Model):
    worker = models.ForeignKey(
        to=Worker,
        verbose_name="Сотрудник",
        on_delete=models.PROTECT,  
        related_name="reports"  
    )
    jtitle = models.ForeignKey(
        to=JobTitle,
        verbose_name="Должность",
        related_name="reports",  
        on_delete=models.PROTECT  
    )
    start = models.DateTimeField(
        verbose_name="Начало смены",
        auto_now_add=True  
    )
    finish = models.DateTimeField(
        verbose_name="Время окончания",
        null=True,
        blank=True  
    )

    class Meta:
        verbose_name = "Запись в табеле"
        verbose_name_plural = "Записи в табеле"
        ordering = ["-start"]  

    def __str__(self):
        finish_text = f"finished at {self.finish}" if self.finish else "not finished yet"
        return f"{self.worker.name} started working as {self.jtitle.title} at {self.start} and {finish_text}"
    
    @property
    def duration(self):
        """Вычисляет продолжительность смены"""
        if self.finish:
            return self.finish - self.start
        return None
    
    @property
    def total_payment(self):
        """Вычисляет общую оплату за смену"""
        if self.finish:
            duration_hours = (self.finish - self.start).total_seconds() / 3600
            return duration_hours * self.jtitle.pay_per_hour
        return None