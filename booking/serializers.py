from rest_framework import serializers
from .models import Appointment
from profiles.models import Profile
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class AppointmentSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    employee_name = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ['id', 'user', 'user_name', 'employee', 'employee_name', 'minimum_hours_to_work', 'address', 'phone_number', 'date', 'status','rejection_reason']


    def get_employee_name(self, obj):
        return obj.employee.name  # Assuming the User model has a method get_full_name()
    
    def get_user_name(self, obj):
        return obj.user.name

    def validate_employee(self, value):
        if not User.objects.filter(id=value.id, is_staff=True).exists():  # Assuming staff users are employees
            raise serializers.ValidationError("Invalid employee ID. This user is not an employee.")
        return value
    
    def validate_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("The appointment date cannot be in the past.")
        return value
