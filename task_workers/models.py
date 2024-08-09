from django.db import models
from account.models import UserData
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from datetime import timedelta
from django.utils import timezone
from dashboard.models import SubscriptionIncome  



class WorkCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    work_image = models.ImageField(verbose_name=_("Work Image"), upload_to='work_image/', default="")
    blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Tasker(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.OneToOneField(UserData, on_delete=models.CASCADE, related_name='tasker_profile')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits")]
    )
    aadhar_number = models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', message="Aadhar number must be 12 digits")]
    )
    address = models.TextField()
    work_photo = models.ImageField(verbose_name=_("Work Photo"), upload_to='work_photos/', default="")
    task = models.ForeignKey(WorkCategory, on_delete=models.CASCADE)
    task_fee = models.DecimalField(max_digits=10, decimal_places=2)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    admin_approval = models.BooleanField(default=False)
    subscribed = models.BooleanField(default=False) 
    subscription_type = models.CharField(max_length=10, choices=SUBSCRIPTION_CHOICES, default='monthly')
    subscription_start_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, default=0)


    def __str__(self):
        return self.full_name

    def activate_subscription(self):
        from datetime import timedelta
        from django.utils import timezone
        from .models import SubscriptionIncome, SubscriptionPrice  # Ensure this import is correct

        try:
            price = SubscriptionPrice.objects.get(subscription_type=self.subscription_type).price
        except SubscriptionPrice.DoesNotExist:
            price = 0

        self.subscription_start_date = timezone.now()
        if self.subscription_type == 'monthly':
            self.subscription_end_date = self.subscription_start_date + timedelta(days=30)
            SubscriptionIncome.update_monthly_income(price)
        elif self.subscription_type == 'yearly':
            self.subscription_end_date = self.subscription_start_date + timedelta(days=365)
            SubscriptionIncome.update_yearly_income(price)
        self.subscribed = True
        self.save()

    @property
    def formatted_subscription_start_date(self):
        return self.subscription_start_date.date()
    
    @property
    def formatted_subscription_end_date(self):
        return self.subscription_end_date.date()

class SubscriptionPrice(models.Model):
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    SUBSCRIPTION_CHOICES = [
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly'),
    ]

    subscription_type = models.CharField(
        max_length=10,
        choices=SUBSCRIPTION_CHOICES,
        unique=True
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.get_subscription_type_display()} - {self.price}'

    @classmethod
    def get_prices(cls):
        prices = cls.objects.all()
        return {item.subscription_type: item.price for item in prices}
