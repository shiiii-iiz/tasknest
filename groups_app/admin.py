from django.contrib import admin
from .models import Group, GroupMembership, GroupTask, Discussion, Message

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'invite_code', 'member_count', 'created_at']
    search_fields = ['name', 'invite_code']

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'group', 'role', 'joined_at']
    list_filter = ['role']

@admin.register(GroupTask)
class GroupTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'group', 'assigned_to', 'priority', 'status', 'due_date']
    list_filter = ['status', 'priority']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['author', 'discussion', 'is_pinned', 'created_at']
    list_filter = ['is_pinned']
