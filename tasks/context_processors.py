from .models import Notification, Task
from django.utils import timezone

def notifications_processor(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(user=request.user)[:5]

        today = timezone.now().date()
        upcoming = Task.objects.filter(
            user=request.user,
            due_date__gte=today,
            due_date__lte=today + timezone.timedelta(days=3),
            status__in=['pending', 'ongoing']
        ).order_by('due_date')[:3]

        return {
            'unread_notif_count': unread_count,
            'recent_notifications': recent_notifications,
            'upcoming_tasks': upcoming,
        }
    return {}
