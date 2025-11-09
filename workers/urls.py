# workers/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JobTitleViewSet, WorkerViewSet, ReportViewSet

app_name = 'workers'

router = DefaultRouter()
router.register(r'job-titles', JobTitleViewSet, basename='jobtitle')
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]