from django.db import models

# Create your models here.

class Goods(models.Model):
    name = models.CharField(
        verbose_name="Название товара",
        max_length=100
    )
    price = models.IntegerField(
        verbose_name="Цена товара"
    )
    relevant_from = models.DateField(
        verbose_name="Релевантна с",
        null=True,
        blank=True
    )
    relevant_to = models.DateField(
        verbose_name="Релеванта по",
        null=True,
        blank=True
    )


    class Meta:
        ordering = ["id"]
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"{self.name} costs {self.price}"
    


class Services(models.Model):
    name = models.CharField(
        verbose_name="Название услуги",
        max_length=100
    )
    price = models.IntegerField(
        verbose_name="Цена услуги"
    )

    relevant_from = models.DateField(
        verbose_name="Релевантна с",
        null=True,
        blank=True
    )
    relevant_to = models.DateField(
        verbose_name="Релеванта по",
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return f"{self.name} costs {self.price}"
    

