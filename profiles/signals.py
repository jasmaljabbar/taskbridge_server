import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile
from account.models import UserData

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, email=instance.email)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.email = instance.email
    instance.profile.save()
    logger.info(f"{instance}'s profile created")

@receiver(post_save, sender=Profile)
def update_user_profile_pic(sender, instance, **kwargs):
    user = instance.user
    if user.profile_pic != instance.profile_photo:  # Update only if there's a change
        user.profile_pic = instance.profile_photo
        user.save(update_fields=['profile_pic'])  # Only update profile_pic field
