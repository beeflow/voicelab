from django.contrib import admin
from django.urls import path

from rest_api import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/upload', views.FileUploadView.as_view(), name='upload_file'),
    path('api/v1/waveform/<uuid:id>', views.WaveformView.as_view(), name='get_waveform'),
    path('api/v1/tasks/<int:page>', views.TasksView.as_view(), name='get_tasks'),
    path('api/v1/tasks', views.TasksView.as_view(), name='get_first_page_tasks'),
    path('api/v1/tasks/<uuid:task_id>', views.TaskView.as_view(), name='get_task'),
]
