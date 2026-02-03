from django.urls import path
from .views import CSVUploadView, HistoryView, ReportView

urlpatterns = [
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
    path('history/', HistoryView.as_view(), name='history'),
    path('report/<int:pk>/', ReportView.as_view(), name='report'),
]
