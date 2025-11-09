# documentation/admin.py
from django.contrib import admin
from .models import Nationality, Document


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ['nationality', 'code', 'documents_count', 'guests_count']
    search_fields = ['nationality', 'code']
    
    def documents_count(self, obj):
        return obj.documents.count()
    documents_count.short_description = 'Документов'
    
    def guests_count(self, obj):
        return obj.guests.count()
    guests_count.short_description = 'Гостей'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'IIN', 'full_name', 'document_type', 'number',
        'nationality', 'expiry_date', 'is_expired', 'uploaded_at'
    ]
    list_filter = ['document_type', 'nationality', 'uploaded_at']
    search_fields = ['IIN', 'first_name', 'last_name', 'number']
    readonly_fields = ['uploaded_at', 'updated_at', 'is_expired', 'days_until_expiry', 'is_expiring_soon']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('nationality', 'IIN', 'first_name', 'last_name', 'middle_name', 'date_of_birth')
        }),
        ('Документ', {
            'fields': ('document_type', 'number', 'issued_date', 'expiry_date', 'issued_by')
        }),
        ('Файлы', {
            'fields': ('file', 'url')
        }),
        ('Статус', {
            'fields': ('is_expired', 'days_until_expiry', 'is_expiring_soon'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Системная информация', {
            'fields': ('uploaded_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        return "✅ Да" if obj.is_expired else "❌ Нет"
    is_expired.short_description = 'Истёк'