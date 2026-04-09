from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_color = models.CharField(max_length=20, default='#f9a8d4')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_initials(self):
        name = self.user.get_full_name()
        if name:
            parts = name.split()
            return ''.join([p[0].upper() for p in parts[:2]])
        return self.user.username[:2].upper()
