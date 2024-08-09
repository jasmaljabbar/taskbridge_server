from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.dispatch import Signal



from common.models import TimeStampedUUIDModel

post_save_user_profile = Signal()

User = get_user_model()

class Gender(models.TextChoices):
    MALE = "Male", _("Male")
    FEMALE = "Female", _("Female")
    OTHER = "Other", _("Other")

class Profile(TimeStampedUUIDModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(verbose_name=_("Email"), max_length=100, unique=True, default='email')
    address = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Phone Number")
    profile_photo = models.ImageField(verbose_name=_("Profile Photo"), upload_to='profile_photos/', default="")
    gender = models.CharField(verbose_name=_("Gender"), choices=Gender.choices, default=Gender.OTHER, max_length=20)
    city = models.CharField(verbose_name=_("City"), max_length=180)
    is_tasker = models.BooleanField(verbose_name=_("Tasker"), default=False, help_text=_("Are you looking for a Tasker?"))

    def __str__(self):
        return f"{self.user.get_full_name()}'s profile"
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        post_save_user_profile.send(sender=self.__class__, instance=self)
