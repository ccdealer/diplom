# workers/views.py
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from datetime import timedelta

from .models import JobTitle, Worker, Report
from .serializers import (
    JobTitleListSerializer, JobTitleDetailSerializer, JobTitleCreateUpdateSerializer,
    WorkerListSerializer, WorkerDetailSerializer, WorkerCreateUpdateSerializer,
    ReportListSerializer, ReportDetailSerializer, ReportCreateSerializer, ReportFinishSerializer
)


class JobTitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для должностей
    
    list: Список всех должностей
    retrieve: Детали должности
    create: Создать должность
    update: Обновить должность
    partial_update: Частично обновить должность
    destroy: Удалить должность
    """
    queryset = JobTitle.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['title', 'pay_per_hour']
    ordering = ['title']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return JobTitleListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return JobTitleCreateUpdateSerializer
        return JobTitleDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список должностей",
        operation_description="Получить все должности"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать должность",
        operation_description="Создать новую должность"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Сотрудники по должности",
        operation_description="Получить всех сотрудников с данной должностью"
    )
    @action(detail=True, methods=['get'])
    def workers(self, request, pk=None):
        """Получить сотрудников по должности"""
        job_title = self.get_object()
        workers = job_title.workers.all()
        serializer = WorkerListSerializer(workers, many=True)
        return Response(serializer.data)


class WorkerViewSet(viewsets.ModelViewSet):
    """
    ViewSet для сотрудников
    """
    queryset = Worker.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['main_occupation', 'is_working']
    search_fields = ['name', 'telegram_username']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WorkerListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkerCreateUpdateSerializer
        return WorkerDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список сотрудников",
        operation_description="Получить всех сотрудников"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Создать сотрудника",
        operation_description="Создать нового сотрудника"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Работающие сотрудники",
        operation_description="Получить сотрудников, которые сейчас работают"
    )
    @action(detail=False, methods=['get'])
    def working(self, request):
        """Работающие сотрудники"""
        workers = self.get_queryset().filter(is_working=True)
        serializer = WorkerListSerializer(workers, many=True)
        return Response({
            'count': workers.count(),
            'workers': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Отчёты сотрудника",
        operation_description="Получить все отчёты конкретного сотрудника"
    )
    @action(detail=True, methods=['get'])
    def reports(self, request, pk=None):
        """Получить отчёты сотрудника"""
        worker = self.get_object()
        reports = worker.reports.all()
        serializer = ReportListSerializer(reports, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Статистика сотрудника",
        operation_description="Получить статистику работы сотрудника",
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Статистика сотрудника"""
        worker = self.get_object()
        reports = worker.reports.filter(finish__isnull=False)
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            reports = reports.filter(start__gte=date_from)
        if date_to:
            reports = reports.filter(start__lte=date_to)
        
        total_shifts = reports.count()
        total_hours = sum(
            (r.finish - r.start).total_seconds() / 3600 
            for r in reports
        )
        total_payment = sum(r.total_payment for r in reports)
        
        return Response({
            'worker': WorkerDetailSerializer(worker).data,
            'total_shifts': total_shifts,
            'total_hours': round(total_hours, 2),
            'total_payment': round(total_payment, 2) if total_payment else 0
        })


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet для записей в табеле
    """
    queryset = Report.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['worker', 'jtitle']
    ordering_fields = ['start', 'finish']
    ordering = ['-start']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReportListSerializer
        elif self.action == 'create':
            return ReportCreateSerializer
        return ReportDetailSerializer
    
    @swagger_auto_schema(
        operation_summary="Список отчётов",
        operation_description="Получить все записи в табеле"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Начать смену",
        operation_description="Создать новую запись - начало смены сотрудника"
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Обновить статус сотрудника
        if response.status_code == status.HTTP_201_CREATED:
            report_id = response.data.get('id')
            report = Report.objects.get(id=report_id)
            report.worker.is_working = True
            report.worker.save()
        
        return response
    
    @swagger_auto_schema(
        operation_summary="Активные смены",
        operation_description="Получить все незавершённые смены"
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Активные смены"""
        reports = self.get_queryset().filter(finish__isnull=True)
        serializer = ReportListSerializer(reports, many=True)
        return Response({
            'count': reports.count(),
            'reports': serializer.data
        })
    
    @swagger_auto_schema(
        operation_summary="Завершить смену",
        operation_description="Завершить смену сотрудника",
        request_body=ReportFinishSerializer
    )
    @action(detail=True, methods=['post'])
    def finish(self, request, pk=None):
        """Завершить смену"""
        report = self.get_object()
        
        if report.finish:
            return Response(
                {'error': 'Смена уже завершена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReportFinishSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        finish_time = serializer.validated_data.get('finish', timezone.now())
        report.finish = finish_time
        report.save()
        
        # Обновить статус сотрудника
        report.worker.is_working = False
        report.worker.save()
        
        result_serializer = ReportDetailSerializer(report)
        return Response(result_serializer.data)
    
    @swagger_auto_schema(
        operation_summary="Статистика по отчётам",
        operation_description="Общая статистика по всем отчётам",
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ]
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Общая статистика"""
        queryset = self.get_queryset().filter(finish__isnull=False)
        
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(start__gte=date_from)
        if date_to:
            queryset = queryset.filter(start__lte=date_to)
        
        total_shifts = queryset.count()
        total_hours = sum(
            (r.finish - r.start).total_seconds() / 3600 
            for r in queryset
        )
        total_payment = sum(r.total_payment for r in queryset)
        
        # По должностям
        by_job_title = {}
        for report in queryset:
            title = report.jtitle.title
            if title not in by_job_title:
                by_job_title[title] = {'shifts': 0, 'hours': 0, 'payment': 0}
            
            hours = (report.finish - report.start).total_seconds() / 3600
            by_job_title[title]['shifts'] += 1
            by_job_title[title]['hours'] += hours
            by_job_title[title]['payment'] += report.total_payment
        
        # Округление
        for title in by_job_title:
            by_job_title[title]['hours'] = round(by_job_title[title]['hours'], 2)
            by_job_title[title]['payment'] = round(by_job_title[title]['payment'], 2)
        
        return Response({
            'total_shifts': total_shifts,
            'total_hours': round(total_hours, 2),
            'total_payment': round(total_payment, 2) if total_payment else 0,
            'by_job_title': by_job_title
        })