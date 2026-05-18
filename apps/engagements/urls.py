from django.urls import path
from . import views


urlpatterns = [

    path('', views.dashboard, name='dashboard'),

    path('inbox/', views.inbox, name='inbox'),

    path('engagement/<int:pk>/', views.engagement_detail, name='engagement_detail'),
]