from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.name")
    email = serializers.CharField(source="user.email")

    
    class Meta:
        model = Profile
        fields = ["username", "email", "address", "phone_number", "gender", "id", "city", "profile_photo"]

    def get_full_name(self, obj):
        first_name = obj.user.first_name.title()
        last_name = obj.user.last_name.title()
        return f"{first_name} {last_name}"

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["user", "email", "address", "phone_number", "gender", "city","profile_photo"]

    

