from django.urls import path
from . import views


urlpatterns = [
    path('create-user/', views.create_user, name='create-user'),
    path('users/', views.users_list, name='users-list'),
    path('api/users/', views.users_api, name='users-api'),
    path('api/users/<int:user_id>/', views.get_user_details, name='get-user-details'),
    path('api/users/<int:user_id>/edit/', views.edit_user_details, name='edit-user-details'),
    path('api/users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
    path('manage-groups/', views.manage_groups, name='manage-groups'),
    path('api/groups/', views.groups_api, name='groups-api'),
    path('api/groups/create/', views.create_group, name='create-group'),
    path('api/groups/<int:group_id>/delete/', views.delete_group, name='delete-group'),
]