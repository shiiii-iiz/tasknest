import uuid
from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    invite_code = models.CharField(max_length=12, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cover_color = models.CharField(max_length=20, default='#fda4af')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)

    def get_admin(self):
        membership = self.memberships.filter(role='admin').first()
        return membership.user if membership else self.created_by

    def is_admin(self, user):
        return self.memberships.filter(user=user, role='admin').exists()

    def member_count(self):
        return self.memberships.count()


class GroupMembership(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('member', 'Member')]
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group.name} ({self.role})"


class GroupTask(models.Model):
    PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
    CATEGORY_CHOICES = [
        ('school', 'School'), ('work', 'Work'),
        ('personal', 'Personal'), ('urgent', 'Urgent'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('ongoing', 'Ongoing'), ('completed', 'Completed'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_group_tasks')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_group_tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='work')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-priority']

    def __str__(self):
        return f"[{self.group.name}] {self.title}"

    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date() and self.status != 'completed'


class Discussion(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name='discussion')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Discussion: {self.group.name}"


class Message(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    pinned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pinned_messages'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', 'created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

    def is_reply(self):
        return self.parent is not None
