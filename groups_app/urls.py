from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('join/', views.group_join, name='group_join'),
    path('assigned/', views.assigned_tasks, name='assigned_tasks'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/members/', views.group_members, name='group_members'),
    path('<int:pk>/tasks/', views.group_task_list, name='group_task_list'),
    path('<int:pk>/tasks/create/', views.group_task_create, name='group_task_create'),
    path('<int:pk>/tasks/<int:task_pk>/edit/', views.group_task_edit, name='group_task_edit'),
    path('<int:pk>/tasks/<int:task_pk>/delete/', views.group_task_delete, name='group_task_delete'),
    path('<int:pk>/tasks/<int:task_pk>/status/', views.group_task_update_status, name='group_task_update_status'),
    path('<int:pk>/discussion/', views.discussion_view, name='discussion'),
]
