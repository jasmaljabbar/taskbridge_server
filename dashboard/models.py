from django.db import models

class SubscriptionIncome(models.Model):
    monthly_subscription_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    yearly_subscription_income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Monthly Subscription Income: {self.monthly_subscription_income}, Yearly Subscription Income: {self.yearly_subscription_income}"

    @classmethod
    def update_monthly_income(cls, amount):
        income, created = cls.objects.get_or_create(id=1)
        income.monthly_subscription_income += amount
        income.save()

    @classmethod
    def update_yearly_income(cls, amount):
        income, created = cls.objects.get_or_create(id=1)
        income.yearly_subscription_income += amount
        income.save()
