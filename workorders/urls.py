from django.urls import path
from . import views

app_name = 'workorders'

urlpatterns = [
    path('dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('manage/', views.work_order_manage, name='work_order_manage'),
    path('assign/<int:repair_id>/', views.assign_page, name='assign_page'),
    path('api/workers/', views.api_worker_list, name='api_worker_list'),
    path('api/assign/', views.api_assign, name='api_assign'),
    path('api/reassign/', views.api_reassign, name='api_reassign'),
    path('api/list/', views.api_work_order_list, name='api_work_order_list'),
    path('api/<int:work_order_id>/', views.api_work_order_detail, name='api_work_order_detail'),
    path('api/<int:work_order_id>/accept/', views.api_accept, name='api_accept'),
    path('api/<int:work_order_id>/start/', views.api_start_work, name='api_start_work'),
    path('api/<int:work_order_id>/complete/', views.api_complete, name='api_complete'),
    path('api/<int:work_order_id>/reject/', views.api_reject, name='api_reject'),
]
