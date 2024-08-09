# models.py
from django.db import models
from account.models import UserData

class Chat(models.Model):
    sender = models.ForeignKey(UserData, on_delete=models.SET_NULL, related_name='send_message', null=True, blank=True)
    receiver = models.ForeignKey(UserData, on_delete=models.SET_NULL, related_name='receiver_message', null=True, blank=True)
    message = models.TextField()
    image = models.URLField(blank=True, null=True)
    thread_name = models.CharField(max_length=200, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} - {self.receiver}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    


# class EmployeeNotification(models.Model):
#     appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.appointment.employee.username



# class UserNotification(models.Model):
#     action = models.ForeignKey(EmployeeAction, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     def __str__(self) -> str:
#         return self.action.action
   