# booking/admin.py
from django.contrib import admin
from .models import Agent, Guest, RoomType, Room, RoomCondition, Booking, BookingCard


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'short_title', 'full_title', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['full_title', 'short_title', 'IIN_BIN', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_title', 'short_title', 'IIN_BIN', 'phone')
        }),
        ('Банковские реквизиты', {
            'fields': ('IBAN', 'BIC', 'adress')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'phone', 'email', 'nationality', 'blacklisted', 'created_at']
    list_filter = ['blacklisted', 'gender', 'nationality', 'created_at']
    search_fields = ['first_name', 'last_name', 'middle_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at', 'age']
    filter_horizontal = ['documents']
    
    fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'last_name', 'middle_name', 'date_of_birth', 'age', 'gender')
        }),
        ('Контакты', {
            'fields': ('phone', 'email')
        }),
        ('Документы', {
            'fields': ('nationality', 'documents')
        }),
        ('Чёрный список', {
            'fields': ('blacklisted', 'blacklist_reason'),
            'classes': ('collapse',)
        }),
        ('Дополнительно', {
            'fields': ('notes',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'ФИО'


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'relevant_from', 'relevant_to', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'price', 'description')
        }),
        ('Период актуальности', {
            'fields': ('relevant_from', 'relevant_to')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'room', 'floor', 'is_active', 'get_tariffs_count']
    list_filter = ['floor', 'is_active']
    search_fields = ['room']
    filter_horizontal = ['room_types']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('room', 'floor', 'is_active')
        }),
        ('Тарифы', {
            'fields': ('room_types',)
        }),
    )
    
    def get_tariffs_count(self, obj):
        return obj.room_types.count()
    get_tariffs_count.short_description = 'Тарифов'


@admin.register(RoomCondition)
class RoomConditionAdmin(admin.ModelAdmin):
    list_display = ['id', 'condition', 'color', 'is_available']
    list_filter = ['is_available']
    search_fields = ['condition']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'guest', 'room', 'status', 'check_in', 
        'check_out', 'created_by', 'created_at'
    ]
    list_filter = ['status', 'check_in', 'check_out', 'created_at']
    search_fields = [
        'guest__first_name', 'guest__last_name', 
        'agent__full_title', 'note'
    ]
    readonly_fields = ['created_at', 'updated_at', 'duration']
    
    fieldsets = (
        ('Бронирование', {
            'fields': ('guest', 'agent', 'room', 'room_condition')
        }),
        ('Даты', {
            'fields': ('check_in', 'check_out', 'duration')
        }),
        ('Статус', {
            'fields': ('status',)
        }),
        ('Дополнительно', {
            'fields': ('created_by', 'note')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(BookingCard)
class BookingCardAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'primary_guest', 'status', 'total_amount', 
        'total_bookings', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['primary_guest__first_name', 'primary_guest__last_name']
    readonly_fields = [
        'created_at', 'updated_at', 'total_bookings', 
        'total_goods_amount', 'total_services_amount'
    ]
    filter_horizontal = ['bookings', 'goods', 'services']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('primary_guest', 'status', 'total_amount')
        }),
        ('Бронирования', {
            'fields': ('bookings', 'total_bookings')
        }),
        ('Товары и услуги', {
            'fields': ('goods', 'total_goods_amount', 'services', 'total_services_amount')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )