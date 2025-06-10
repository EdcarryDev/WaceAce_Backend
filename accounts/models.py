from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_user_topics_selected = models.BooleanField(default=False)
    selected_topics = models.JSONField(default=dict, blank=True, help_text="Dictionary of selected subjects and their topics")
    school_name = models.CharField(max_length=255, blank=True, null=True)
    exam_year = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create or update user profile when a user is created or updated.
    Uses transaction.atomic to ensure data consistency.
    """
    if created:
        with transaction.atomic():
            UserProfile.objects.create(user=instance)
    else:
        # Ensure profile exists even if it wasn't created during user creation
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
