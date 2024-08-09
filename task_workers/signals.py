# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Tasker
from account.models import UserData

@receiver(post_save, sender=Tasker)
def update_userdata(sender, instance, **kwargs):
    if instance.subscribed:
        user = instance.user
        user.is_staff = False
        # Remove user.payment_time = True from here
        user.save()
