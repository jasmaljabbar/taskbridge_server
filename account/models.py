from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    use_in_migration = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is Required")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff = True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser = True")

        return self.create_user(email, password, **extra_fields)

class UserData(AbstractUser):
    username = None  # Disable username for email-based authentication
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Full Name"))
    email = models.EmailField(max_length=100, unique=True, verbose_name=_("Email Address"))
    otp = models.CharField(
        max_length=6, 
        blank=True, 
        null=True, 
        validators=[RegexValidator(r'^\d{6}$', message=_("OTP must be a 6-digit number."))]
    )
    otp_time = models.DateTimeField(blank=True, null=True, verbose_name=_("OTP Generated Time"))
    date_joined = models.DateTimeField(auto_now_add=True)
    requested_to_tasker = models.BooleanField(default=False, verbose_name=_("Requested Tasker"))
    payment_pending = models.BooleanField(default=False, verbose_name=_("Payment Pending"))
    blocked_for_tasker = models.BooleanField(default=False, verbose_name=_("Blocked for Tasker"))
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, verbose_name=_("Is Verified"))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_pic = models.URLField(max_length=255, null=True, blank=True, verbose_name=_("Profile Picture URL"))

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.name if self.name else self.email



