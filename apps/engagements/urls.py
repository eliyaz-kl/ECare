from django.urls import path
from . import views


urlpatterns = [

    path('', views.dashboard, name='dashboard'),

    path('inbox/', views.inbox, name='inbox'),

    path('assigned/', views.assigned, name='assigned'),

    path('resolved/', views.resolved, name='resolved'),

    path('api/engagements/<int:pk>/categorize/', views.categorize_engagement, name='categorize_engagement'),

    path('engagement/<int:pk>/', views.engagement_detail, name='engagement_detail'),
]
