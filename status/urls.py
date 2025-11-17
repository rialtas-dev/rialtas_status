from django.urls import path
from . import views

app_name = 'status'

urlpatterns = [
    path('', views.status_page, name='status_page'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('api/service/<int:service_id>/history/', views.service_history_json, name='service_history_json'),
]