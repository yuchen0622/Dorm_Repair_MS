from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('stats/', views.review_stats, name='review_stats'),
    path('create/<int:work_order_id>/', views.review_create, name='review_create'),
    path('api/create/', views.api_review_create, name='api_review_create'),
    path('api/<int:review_id>/', views.api_review_detail, name='api_review_detail'),
    path('api/list/', views.api_review_list, name='api_review_list'),
    path('api/stats/', views.api_review_stats, name='api_review_stats'),
    path('api/ranking/', views.api_worker_ranking, name='api_worker_ranking'),
]
