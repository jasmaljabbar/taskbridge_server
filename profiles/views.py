from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .exceptions import ProfileNotFound
from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer, UpdateProfileSerializer

class GetProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfileJSONRenderer]

    def get(self, request):
        user = request.user
        user_profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(user_profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UpdateProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [ProfileJSONRenderer]
    serializer_class = UpdateProfileSerializer

    def put(self, request):
        try:
            user_profile = Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            raise ProfileNotFound("Profile not found")

        data = request.data 
        serializer = UpdateProfileSerializer(instance=user_profile, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
