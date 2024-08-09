from rest_framework import serializers
from .models import Tasker, WorkCategory
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']

class WorkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkCategory
        fields = ['id', 'name', 'description', 'work_image','blocked']

        


class TaskerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(queryset=WorkCategory.objects.all())
    task_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    city = serializers.CharField(max_length=50)
    state = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)
    work_photo = serializers.ImageField(required=False)

    class Meta:
        model = Tasker
        fields = [
            'user', 'full_name', 'phone_number', 'aadhar_number', 'task', 'task_fee',
            'city', 'state', 'address', 'work_photo','subscribed'
        ]

    def create(self, validated_data):
        user = self.context['request'].user
        tasker = Tasker.objects.create(user=user, **validated_data)
        return tasker

    

class TaskerFetchingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    task = WorkCategorySerializer(read_only=True)
    profile_pic = serializers.ImageField(source='user.profile_pic', read_only=True)

    class Meta:
        model = Tasker
        fields = [
            'user', 'full_name','profile_pic', 'phone_number', 'aadhar_number', 'task', 'task_fee',
            'city', 'state', 'address', 'work_photo'
        ]




class TaskerUpdateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    task = serializers.PrimaryKeyRelatedField(queryset=WorkCategory.objects.all(), write_only=True, required=False)
    task_fee = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True, required=False)
    city = serializers.CharField(max_length=50, required=False)
    state = serializers.CharField(max_length=50, required=False)
    address = serializers.CharField(max_length=255, required=False)
    work_photo = serializers.ImageField(required=False)

    class Meta:
        model = Tasker
        fields = [
            'user', 'full_name', 'phone_number', 'aadhar_number', 'task', 'task_fee',
            'city', 'state', 'address', 'work_photo'
        ]

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.aadhar_number = validated_data.get('aadhar_number', instance.aadhar_number)
        instance.city = validated_data.get('city', instance.city)
        instance.state = validated_data.get('state', instance.state)
        instance.address = validated_data.get('address', instance.address)
        instance.work_photo = validated_data.get('work_photo', instance.work_photo)

        task = validated_data.get('task')
        task_fee = validated_data.get('task_fee')

        if task is not None:
            instance.task = task

        if task_fee is not None:
            instance.task_fee = task_fee

        instance.save()
        return instance