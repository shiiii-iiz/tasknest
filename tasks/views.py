from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
import json
import calendar
from .models import Task, Notification
from .forms import TaskForm
from groups_app.models import GroupTask


@login_required
def dashboard(request):
    tasks = Task.objects.filter(user=request.user)
    today = timezone.now().date()

    total = tasks.count()
    pending = tasks.filter(status='pending').count()
    ongoing = tasks.filter(status='ongoing').count()
    completed = tasks.filter(status='completed').count()
    overdue = tasks.filter(due_date__lt=today, status__in=['pending', 'ongoing']).count()

    recent_tasks = tasks.exclude(status='completed').order_by('due_date')[:5]
    upcoming = tasks.filter(
        due_date__gte=today,
        due_date__lte=today + timezone.timedelta(days=7),
        status__in=['pending', 'ongoing']
    ).order_by('due_date')

    # Generate notifications
    _generate_notifications(request.user)

    # Assigned group tasks
    assigned_group_tasks = GroupTask.objects.filter(
        assigned_to=request.user
    ).select_related('group').exclude(status='completed')[:5]

    context = {
        'total': total,
        'pending': pending,
        'ongoing': ongoing,
        'completed': completed,
        'overdue': overdue,
        'recent_tasks': recent_tasks,
        'upcoming': upcoming,
        'assigned_group_tasks': assigned_group_tasks,
        'today': today,
    }
    return render(request, 'tasks/dashboard.html', context)


def _generate_notifications(user):
    today = timezone.now().date()
    tomorrow = today + timezone.timedelta(days=1)

    tasks = Task.objects.filter(user=user, status__in=['pending', 'ongoing'])
    for task in tasks:
        # Due soon
        if task.due_date == tomorrow:
            Notification.objects.get_or_create(
                user=user, task=task, notif_type='due_soon',
                defaults={
                    'title': f'Task Due Tomorrow!',
                    'message': f'"{task.title}" is due tomorrow. Don\'t forget to complete it!',
                }
            )
        # Overdue
        if task.due_date < today:
            Notification.objects.get_or_create(
                user=user, task=task, notif_type='overdue',
                defaults={
                    'title': f'Task Overdue!',
                    'message': f'"{task.title}" was due on {task.due_date}. Please update its status.',
                }
            )


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    category = request.GET.get('category', '')
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', '')
    search = request.GET.get('search', '')

    if category:
        tasks = tasks.filter(category=category)
    if priority:
        tasks = tasks.filter(priority=priority)
    if status:
        tasks = tasks.filter(status=status)
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))

    context = {
        'tasks': tasks,
        'category': category,
        'priority': priority,
        'status': status,
        'search': search,
        'categories': Task.CATEGORY_CHOICES,
        'priorities': Task.PRIORITY_CHOICES,
        'statuses': Task.STATUS_CHOICES,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, f'Task "{task.title}" created successfully! 🌸')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task updated successfully! 🌸')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Edit', 'task': task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if task.status == 'completed':
        task.status = 'pending'
    else:
        task.status = 'completed'
    task.save()
    return JsonResponse({'status': task.status, 'success': True})


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user)
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'tasks/notifications.html', {'notifications': notifs})


@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications')


@login_required
def calendar_view(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    personal_tasks = Task.objects.filter(
        user=request.user,
        due_date__year=year,
        due_date__month=month
    )

    group_tasks = GroupTask.objects.filter(
        group__memberships__user=request.user,
        due_date__year=year,
        due_date__month=month
    ).distinct()

    tasks_by_day = {}
    for task in personal_tasks:
        day = task.due_date.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append({'title': task.title, 'type': 'personal', 'priority': task.priority, 'status': task.status})

    for task in group_tasks:
        day = task.due_date.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append({'title': task.title, 'type': 'group', 'priority': task.priority, 'status': task.status})

    # Prev/next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    context = {
        'calendar': cal,
        'month_name': month_name,
        'year': year,
        'month': month,
        'today': today,
        'tasks_by_day': tasks_by_day,
        'tasks_by_day_json': json.dumps(tasks_by_day),
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }
    return render(request, 'tasks/calendar.html', context)
