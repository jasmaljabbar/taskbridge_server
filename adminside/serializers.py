from rest_framework import serializers
from account.models import UserData
from task_workers.models import SubscriptionPrice

class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = [
            "id",
            "name",
            "email",
            "date_joined",
            "is_admin",
            "is_active",
            "is_staff",
            "is_superuser",
            "requested_to_tasker",
            "blocked_for_tasker",
            "profile_pic",
        ]


class SubscriptionPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPrice
        fields = ['subscription_type', 'price']