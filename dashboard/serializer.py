from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from task_workers.models import Tasker,WorkCategory,SubscriptionPrice
from profiles.models import Profile
from booking.models import Appointment
from account.models import UserData


class EmployeeIndvualSerializers(ModelSerializer):
    service = WorkCategory
    class Meta:
        model = Tasker
        fields = ['id','user', 'full_name', 'phone_number', 'aadhar_number', 'task', 'task_fee',
            'city', 'state', 'address', 'work_photo']
    read_only_fields = ["id"]



class UserIndvualSerializers(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  

    class Meta:
        model = Profile
        fields = ['id', 'user', 'phone_number', 'profile_photo']
        read_only_fields = ["id"]


class CountSerializer(serializers.Serializer):
    users_count = serializers.IntegerField()
    workers_count = serializers.IntegerField()



class TaskerSubscriptionSerializer(serializers.ModelSerializer):
    subscription_price = serializers.SerializerMethodField()

    class Meta:
        model = Tasker
        fields = ['full_name', 'subscription_start_date', 'subscription_type', 'subscription_price']

    def get_subscription_price(self, obj):
        price = SubscriptionPrice.objects.filter(subscription_type=obj.subscription_type).first()
        return price.price if price else None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['name']

class BookingAppointmentSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Appointment
        fields = ['user', 'minimum_hours_to_work', 'date']