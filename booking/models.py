from django.db import models
from account.models import UserData
from task_workers.models import Tasker
from profiles.models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()

class Appointment(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    COMPLETE = 'complete'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (COMPLETE, 'Complete'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_appointments')
    minimum_hours_to_work = models.IntegerField()
    address = models.TextField()
    phone_number = models.CharField(max_length=15)  
    date = models.DateField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    rejection_reason = models.CharField(max_length=100, null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date}"

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"


