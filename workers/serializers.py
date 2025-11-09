# workers/serializers.py
from rest_framework import serializers
from .models import JobTitle, Worker, Report
from django.contrib.auth.models import User
from django.utils import timezone


# ==================== JobTitle Serializers ====================

class JobTitleListSerializer(serializers.ModelSerializer):
    """Список должностей"""
    workers_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = JobTitle
        fields = ['id', 'title', 'pay_per_hour', 'workers_count']
        read_only_fields = ['id']
    
    def get_workers_count(self, obj):
        return obj.workers.count()


class JobTitleDetailSerializer(serializers.ModelSerializer):
    """Детали должности"""
    workers_count = serializers.SerializerMethodField(read_only=True)
    reports_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = JobTitle
        fields = '__all__'
        read_only_fields = ['id']
    
    def get_workers_count(self, obj):
        return obj.workers.count()
    
    def get_reports_count(self, obj):
        return obj.reports.count()


class JobTitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление должности"""
    
    class Meta:
        model = JobTitle
        fields = ['title', 'pay_per_hour']
    
    def validate_pay_per_hour(self, value):
        if value <= 0:
            raise serializers.ValidationError("Оплата должна быть больше нуля")
        return value


# ==================== Worker Serializers ====================

class WorkerListSerializer(serializers.ModelSerializer):
    """Список сотрудников"""
    main_occupation_title = serializers.CharField(
        source='main_occupation.title', 
        read_only=True, 
        allow_null=True
    )
    
    class Meta:
        model = Worker
        fields = [
            'id', 'name', 'main_occupation', 'main_occupation_title',
            'telegram_username', 'is_working', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class WorkerDetailSerializer(serializers.ModelSerializer):
    """Детали сотрудника"""
    main_occupation_title = serializers.CharField(
        source='main_occupation.title', 
        read_only=True, 
        allow_null=True
    )
    reports_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Worker
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
    
    def get_reports_count(self, obj):
        return obj.reports.count()


class WorkerCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/обновление сотрудника"""
    
    class Meta:
        model = Worker
        fields = [
            'name', 'main_occupation', 'telegram_id', 
            'telegram_username', 'is_working', 'user'
        ]
    
    def validate_telegram_id(self, value):
        """Проверка уникальности telegram_id"""
        instance = self.instance
        if Worker.objects.filter(telegram_id=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("Сотрудник с таким Telegram ID уже существует")
        return value


# ==================== Report Serializers ====================

class ReportListSerializer(serializers.ModelSerializer):
    """Список записей в табеле"""
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    job_title = serializers.CharField(source='jtitle.title', read_only=True)
    duration = serializers.DurationField(read_only=True)
    total_payment = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id', 'worker', 'worker_name', 'jtitle', 'job_title',
            'start', 'finish', 'duration', 'total_payment'
        ]
        read_only_fields = ['id', 'start']


class ReportDetailSerializer(serializers.ModelSerializer):
    """Детали записи в табеле"""
    worker_name = serializers.CharField(source='worker.name', read_only=True)
    job_title = serializers.CharField(source='jtitle.title', read_only=True)
    pay_per_hour = serializers.IntegerField(source='jtitle.pay_per_hour', read_only=True)
    duration = serializers.DurationField(read_only=True)
    total_payment = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Report
        fields = '__all__'
        read_only_fields = ['id', 'start']


class ReportCreateSerializer(serializers.ModelSerializer):
    """Создание записи в табеле (начало смены)"""
    
    class Meta:
        model = Report
        fields = ['worker', 'jtitle']
    
    def validate_worker(self, value):
        """Проверка, что у сотрудника нет незавершённой смены"""
        if Report.objects.filter(worker=value, finish__isnull=True).exists():
            raise serializers.ValidationError(
                "У сотрудника уже есть незавершённая смена"
            )
        return value


class ReportFinishSerializer(serializers.Serializer):
    """Завершение смены"""
    finish = serializers.DateTimeField(required=False)
    
    def validate_finish(self, value):
        """Проверка времени окончания"""
        if value and value < self.instance.start:
            raise serializers.ValidationError(
                "Время окончания не может быть раньше начала смены"
            )
        return value