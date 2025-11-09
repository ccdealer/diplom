# ameneties/admin.py
from django.contrib import admin
from .models import Goods, Services


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'relevant_from', 'relevant_to']
    search_fields = ['name']
    list_filter = ['relevant_from', 'relevant_to']
    ordering = ['id']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'price')
        }),
        ('Период актуальности', {
            'fields': ('relevant_from', 'relevant_to')
        }),
    )


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'relevant_from', 'relevant_to']
    search_fields = ['name']
    list_filter = ['relevant_from', 'relevant_to']
    ordering = ['id']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'price')
        }),
        ('Период актуальности', {
            'fields': ('relevant_from', 'relevant_to')
        }),
    )