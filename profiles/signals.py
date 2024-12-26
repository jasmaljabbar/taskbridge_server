import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile
from account.models import UserData

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, email=instance.email)
    else:
        profile = instance.profile
        if profile.email != instance.email:
            profile.email = instance.email
            profile.save()


@receiver(post_save, sender=Profile)
def update_user_profile_pic(sender, instance, **kwargs):
    user = instance.user
    if hasattr(user, 'profile_pic') and user.profile_pic != instance.profile_photo:
        user.profile_pic = instance.profile_photo
        user.save(update_fields=['profile_pic'])


