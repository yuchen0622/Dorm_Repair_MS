from django.urls import path
from . import views

app_name = 'repairs'

urlpatterns = [
    path('my/', views.my_repairs, name='my_repairs'),
    path('create/', views.repair_create, name='repair_create'),
    path('api/list/', views.api_repair_list, name='api_repair_list'),
    path('api/stats/', views.api_repair_stats, name='api_repair_stats'),
    path('api/create/', views.api_repair_create, name='api_repair_create'),
    path('api/<int:repair_id>/', views.api_repair_detail, name='api_repair_detail'),
    path('api/<int:repair_id>/update/', views.api_repair_update, name='api_repair_update'),
    path('api/<int:repair_id>/delete/', views.api_repair_delete, name='api_repair_delete'),
    path('api/<int:repair_id>/upload/', views.api_image_upload, name='api_image_upload'),
    path('api/image/<int:image_id>/delete/', views.api_image_delete, name='api_image_delete'),
]
