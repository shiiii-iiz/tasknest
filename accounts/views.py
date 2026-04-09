from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import RegisterForm, LoginForm
from .models import Profile


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to TaskNest, {user.first_name}! 🌸')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 🌸')
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. See you soon! 🌸')
    return redirect('login')


@login_required
def profile_view(request):
    from groups_app.models import GroupMembership
    from tasks.models import Task

    profile, _ = Profile.objects.get_or_create(user=request.user)
    today       = timezone.now().date()

    tasks = Task.objects.filter(user=request.user)
    task_pending   = tasks.filter(status='pending').count()
    task_ongoing   = tasks.filter(status='ongoing').count()
    task_completed = tasks.filter(status='completed').count()
    task_overdue   = tasks.filter(due_date__lt=today, status__in=['pending', 'ongoing']).count()

    memberships = GroupMembership.objects.filter(
        user=request.user
    ).select_related('group').order_by('-joined_at')

    profile_fields = [
        ('Full Name',  request.user.get_full_name() or '—'),
        ('Username',   f'@{request.user.username}'),
        ('Email',      request.user.email or '—'),
        ('Member Since', request.user.date_joined.strftime('%B %d, %Y')),
        ('Total Tasks',  str(tasks.count())),
        ('Groups Joined', str(memberships.count())),
    ]

    context = {
        'profile':        profile,
        'profile_fields': profile_fields,
        'task_pending':   task_pending,
        'task_ongoing':   task_ongoing,
        'task_completed': task_completed,
        'task_overdue':   task_overdue,
        'memberships':    memberships,
    }
    return render(request, 'accounts/profile.html', context)
