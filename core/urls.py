from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download_video, name='download_video'),
    path('upload/', views.upload_video, name='upload_video'),
    path('process/', views.process_video, name='process_video'),
    path('delete/', views.delete_video, name='delete_video'),
    path('add-command/', views.add_custom_command, name='add_custom_command'),
    path('get-progress/<str:task_id>/', views.get_progress, name='get_progress'),
]
