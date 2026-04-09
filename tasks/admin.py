from django.contrib import admin
from .models import Task, Notification

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'category', 'due_date']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['title', 'user__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notif_type', 'is_read', 'created_at']
    list_filter = ['notif_type', 'is_read']
