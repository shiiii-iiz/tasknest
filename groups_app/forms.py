from django import forms
from django.contrib.auth.models import User
from .models import Group, GroupTask, Message


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'cover_color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Group name...'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'What is this group about?'
            }),
            'cover_color': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('#fda4af', '🌸 Rose Pink'),
                ('#f9a8d4', '💗 Bubblegum'),
                ('#fbcfe8', '🩷 Blush'),
                ('#c4b5fd', '💜 Lavender'),
                ('#a5f3fc', '🩵 Sky Blue'),
                ('#86efac', '💚 Mint'),
                ('#fde68a', '💛 Butter'),
                ('#fed7aa', '🍑 Peach'),
            ]),
        }


class JoinGroupForm(forms.Form):
    invite_code = forms.CharField(
        max_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter invite code...',
            'style': 'text-transform:uppercase; letter-spacing:4px; font-weight:700; font-size:1.1rem;',
            'autocomplete': 'off',
        })
    )

    def clean_invite_code(self):
        return self.cleaned_data['invite_code'].upper().strip()


class GroupTaskForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = GroupTask
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'status', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task title...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Task description...'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        if group:
            user_ids = group.memberships.values_list('user_id', flat=True)
            self.fields['assigned_to'].queryset = User.objects.filter(id__in=user_ids)
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = '— Unassigned —'


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write a message to your group...',
            })
        }


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write a reply...',
            })
        }
