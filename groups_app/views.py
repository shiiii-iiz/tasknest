from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Group, GroupMembership, GroupTask, Discussion, Message
from .forms import GroupForm, JoinGroupForm, GroupTaskForm, MessageForm, ReplyForm
from tasks.models import Notification


# ─── Helpers ────────────────────────────────────────────────────────────────

def _get_membership(user, group):
    return GroupMembership.objects.filter(user=user, group=group).first()

def _require_member(user, group):
    return GroupMembership.objects.filter(user=user, group=group).exists()

def _require_admin(user, group):
    return GroupMembership.objects.filter(user=user, group=group, role='admin').exists()


# ─── Group CRUD ─────────────────────────────────────────────────────────────

@login_required
def group_list(request):
    memberships = GroupMembership.objects.filter(
        user=request.user
    ).select_related('group', 'group__created_by').order_by('-group__created_at')
    return render(request, 'groups_app/group_list.html', {'memberships': memberships})


@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            GroupMembership.objects.create(group=group, user=request.user, role='admin')
            Discussion.objects.create(group=group)
            django_messages.success(request, f'Group "{group.name}" created! Share code: {group.invite_code} 🌸')
            return redirect('group_detail', pk=group.pk)
    else:
        form = GroupForm()
    return render(request, 'groups_app/group_form.html', {'form': form, 'action': 'Create'})


@login_required
def group_join(request):
    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['invite_code']
            try:
                group = Group.objects.get(invite_code=code)
                if GroupMembership.objects.filter(group=group, user=request.user).exists():
                    django_messages.warning(request, 'You are already a member of this group.')
                else:
                    GroupMembership.objects.create(group=group, user=request.user, role='member')
                    # Ensure discussion exists
                    Discussion.objects.get_or_create(group=group)
                    django_messages.success(request, f'Joined "{group.name}" successfully! 🌸')
                return redirect('group_detail', pk=group.pk)
            except Group.DoesNotExist:
                django_messages.error(request, 'Invalid invite code. Please try again.')
    else:
        form = JoinGroupForm()
    return render(request, 'groups_app/group_join.html', {'form': form})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = _get_membership(request.user, group)
    if not membership:
        django_messages.error(request, 'You are not a member of this group.')
        return redirect('group_list')

    tasks = GroupTask.objects.filter(group=group)
    pending_count = tasks.filter(status='pending').count()
    ongoing_count = tasks.filter(status='ongoing').count()
    completed_count = tasks.filter(status='completed').count()
    recent_tasks = tasks.exclude(status='completed').order_by('due_date')[:5]
    members = GroupMembership.objects.filter(group=group).select_related('user')

    # Pinned messages
    try:
        discussion = group.discussion
        pinned = Message.objects.filter(discussion=discussion, is_pinned=True, parent=None).select_related('author')
        recent_messages = Message.objects.filter(discussion=discussion, parent=None).select_related('author').order_by('-created_at')[:3]
    except Discussion.DoesNotExist:
        pinned = []
        recent_messages = []

    context = {
        'group': group,
        'membership': membership,
        'is_admin': membership.role == 'admin',
        'members': members,
        'pending_count': pending_count,
        'ongoing_count': ongoing_count,
        'completed_count': completed_count,
        'recent_tasks': recent_tasks,
        'pinned_messages': pinned,
        'recent_messages': recent_messages,
    }
    return render(request, 'groups_app/group_detail.html', context)


@login_required
def group_members(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = _get_membership(request.user, group)
    if not membership:
        return redirect('group_list')
    members = GroupMembership.objects.filter(group=group).select_related('user')
    return render(request, 'groups_app/group_members.html', {
        'group': group,
        'membership': membership,
        'is_admin': membership.role == 'admin',
        'members': members,
    })


# ─── Group Tasks ─────────────────────────────────────────────────────────────

@login_required
def group_task_list(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = _get_membership(request.user, group)
    if not membership:
        return redirect('group_list')

    tasks = GroupTask.objects.filter(group=group).select_related('assigned_to', 'created_by')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)

    context = {
        'group': group,
        'tasks': tasks,
        'membership': membership,
        'is_admin': membership.role == 'admin',
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'statuses': GroupTask.STATUS_CHOICES,
        'priorities': GroupTask.PRIORITY_CHOICES,
    }
    return render(request, 'groups_app/group_task_list.html', context)


@login_required
def group_task_create(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = _get_membership(request.user, group)
    if not membership:
        return redirect('group_list')

    if request.method == 'POST':
        form = GroupTaskForm(request.POST, group=group)
        if form.is_valid():
            task = form.save(commit=False)
            task.group = group
            task.created_by = request.user
            task.save()
            if task.assigned_to and task.assigned_to != request.user:
                Notification.objects.create(
                    user=task.assigned_to,
                    title='New Task Assigned!',
                    message=f'You were assigned "{task.title}" in group "{group.name}".',
                    notif_type='assigned',
                )
            django_messages.success(request, f'Task "{task.title}" created! 🌸')
            return redirect('group_task_list', pk=group.pk)
    else:
        form = GroupTaskForm(group=group)

    return render(request, 'groups_app/group_task_form.html', {
        'form': form, 'group': group, 'action': 'Create',
        'membership': membership, 'is_admin': membership.role == 'admin',
    })


@login_required
def group_task_edit(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)
    membership = _get_membership(request.user, group)
    if not membership:
        return redirect('group_list')

    if request.method == 'POST':
        form = GroupTaskForm(request.POST, instance=task, group=group)
        if form.is_valid():
            form.save()
            django_messages.success(request, 'Task updated! 🌸')
            return redirect('group_task_list', pk=group.pk)
    else:
        form = GroupTaskForm(instance=task, group=group)

    return render(request, 'groups_app/group_task_form.html', {
        'form': form, 'group': group, 'task': task, 'action': 'Edit',
        'membership': membership, 'is_admin': membership.role == 'admin',
    })


@login_required
def group_task_delete(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)
    membership = _get_membership(request.user, group)
    if not membership:
        return redirect('group_list')
    if request.method == 'POST':
        task.delete()
        django_messages.success(request, 'Task deleted.')
        return redirect('group_task_list', pk=group.pk)
    return render(request, 'groups_app/group_task_confirm_delete.html', {
        'group': group, 'task': task, 'membership': membership,
    })


@login_required
def group_task_update_status(request, pk, task_pk):
    group = get_object_or_404(Group, pk=pk)
    task = get_object_or_404(GroupTask, pk=task_pk, group=group)
    if not _require_member(request.user, group):
        return JsonResponse({'error': 'Not a member'}, status=403)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'ongoing', 'completed']:
            task.status = new_status
            task.save()
            return JsonResponse({'status': task.status, 'success': True})
    return JsonResponse({'error': 'Invalid'}, status=400)


# ─── Discussion ──────────────────────────────────────────────────────────────

@login_required
def discussion_view(request, pk):
    group = get_object_or_404(Group, pk=pk)
    membership = _get_membership(request.user, group)
    if not membership:
        return redirect('group_list')

    discussion, _ = Discussion.objects.get_or_create(group=group)
    pinned = Message.objects.filter(
        discussion=discussion, is_pinned=True, parent=None
    ).select_related('author').order_by('created_at')

    all_messages = Message.objects.filter(
        discussion=discussion, parent=None
    ).select_related('author').prefetch_related(
        'replies', 'replies__author'
    ).order_by('created_at')

    # Separate non-pinned messages for the main feed
    main_messages = all_messages.filter(is_pinned=False)

    form = MessageForm()
    reply_form = ReplyForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'post':
            form = MessageForm(request.POST)
            if form.is_valid():
                msg = form.save(commit=False)
                msg.discussion = discussion
                msg.author = request.user
                msg.save()
                django_messages.success(request, 'Message posted! 🌸')
                return redirect('discussion', pk=group.pk)

        elif action == 'reply':
            parent_id = request.POST.get('parent_id')
            parent = get_object_or_404(Message, pk=parent_id, discussion=discussion)
            reply_form = ReplyForm(request.POST)
            if reply_form.is_valid():
                reply = reply_form.save(commit=False)
                reply.discussion = discussion
                reply.author = request.user
                reply.parent = parent
                reply.save()
                django_messages.success(request, 'Reply posted! 🌸')
                return redirect('discussion', pk=group.pk)

        elif action == 'pin' and membership.role == 'admin':
            msg_id = request.POST.get('message_id')
            msg = get_object_or_404(Message, pk=msg_id, discussion=discussion)
            msg.is_pinned = not msg.is_pinned
            msg.pinned_by = request.user if msg.is_pinned else None
            msg.save()
            label = 'pinned' if msg.is_pinned else 'unpinned'
            django_messages.success(request, f'Message {label}!')
            return redirect('discussion', pk=group.pk)

        elif action == 'delete':
            msg_id = request.POST.get('message_id')
            msg = get_object_or_404(Message, pk=msg_id, discussion=discussion)
            if msg.author == request.user or membership.role == 'admin':
                msg.delete()
                django_messages.success(request, 'Message deleted.')
            return redirect('discussion', pk=group.pk)

    context = {
        'group': group,
        'membership': membership,
        'is_admin': membership.role == 'admin',
        'pinned_messages': pinned,
        'main_messages': main_messages,
        'form': form,
        'reply_form': reply_form,
    }
    return render(request, 'groups_app/discussion.html', context)


# ─── Assigned Tasks ──────────────────────────────────────────────────────────

@login_required
def assigned_tasks(request):
    tasks = GroupTask.objects.filter(
        assigned_to=request.user
    ).select_related('group', 'created_by').order_by('due_date')
    status_filter = request.GET.get('status', '')
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    return render(request, 'groups_app/assigned_tasks.html', {
        'tasks': tasks,
        'status_filter': status_filter,
        'statuses': GroupTask.STATUS_CHOICES,
    })
