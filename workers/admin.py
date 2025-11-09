# workers/admin.py
from django.contrib import admin
from .models import JobTitle, Worker, Report


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'pay_per_hour', 'workers_count']
    search_fields = ['title']
    
    def workers_count(self, obj):
        return obj.workers.count()
    workers_count.short_description = 'Сотрудников'


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'main_occupation', 'telegram_username',
        'is_working', 'created_at'
    ]
    list_filter = ['is_working', 'main_occupation', 'created_at']
    search_fields = ['name', 'telegram_username']
    readonly_fields = ['created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'worker', 'jtitle', 'start', 'finish',
        'get_duration', 'get_payment'
    ]
    list_filter = ['jtitle', 'start']
    search_fields = ['worker__name']
    readonly_fields = ['start', 'duration', 'total_payment']
    
    def get_duration(self, obj):
        if obj.duration:
            total_seconds = obj.duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
        return "-"
    get_duration.short_description = 'Длительность'
    
    def get_payment(self, obj):
        if obj.total_payment:
            return f"{obj.total_payment:.2f} ₸"
        return "-"
    get_payment.short_description = 'Оплата'