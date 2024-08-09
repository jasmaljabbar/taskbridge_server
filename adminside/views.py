from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from account.models import UserData
from task_workers.serializers import WorkCategorySerializer
from .serializers import UserDataSerializer,SubscriptionPriceSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from task_workers.models import WorkCategory
from task_workers.serializers import TaskerFetchingSerializer
from task_workers.models import Tasker
from task_workers.models import SubscriptionPrice
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.decorators import permission_classes
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet


class AdminLogin(APIView):

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(email=email, password=password)

        if user is not None and user.is_staff:

            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        else:

            return Response(
                {"error": "Invalid credentials or user is not an admin."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class Dashboard(APIView):

    def get(self, request):
        users = UserData.objects.filter(is_superuser=False)
        serializer = UserDataSerializer(users, many=True)
        return Response(serializer.data)
    



class Accepting_request(APIView):

    def post(self, request):
        user_id = request.data.get("id")
        try:
            user = UserData.objects.get(id=user_id)
        except UserData.DoesNotExist:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            tasker = Tasker.objects.get(user=user)
            tasker.admin_approval = True
            user.requested_to_tasker = False
            user.payment_time = True
            user.save()
            tasker.save()
            return Response({"Success": "User Approved"}, status=status.HTTP_200_OK)
        except Tasker.DoesNotExist:
            return Response({"error": "Tasker does not exist for this user"}, status=status.HTTP_404_NOT_FOUND)


            
class TaskerDetails(APIView):
    serializer_class = TaskerFetchingSerializer
    
    def get(self, request):
        user_id = request.query_params.get("id")
        
        
        try:
            user_data = get_object_or_404(UserData, id=user_id)
            tasker = get_object_or_404(Tasker, user=user_data)
            
        except UserData.DoesNotExist:
           
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Tasker.DoesNotExist:
            
            return Response({"error": "Tasker not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(tasker)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Block_user(APIView):

    def post(self, request):
        user_id = request.data.get("id")
        try:
            user = UserData.objects.get(id=user_id)
            user.is_active = not user.is_active
            user.save()
            return Response({"success": "User action completed", "is_active": user.is_active}, status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

        
class Blocking_tasker(APIView):

    def post(self, request):
        user_id = request.data.get("id")
        try:
            user = UserData.objects.get(id=user_id)
            user.blocked_for_tasker = not user.blocked_for_tasker
            user.save()
            return Response({"Success": "User Deleted"}, status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class EditUser(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id):
        user = get_object_or_404(UserData, id=id)
        try:
            user.name = request.data.get("name")
            user.email = request.data.get("email")
            password = request.data.get("password")
            confirm_password = request.data.get("confirm_password")

            # Check if the email already exists for another user
            existing_user = (
                UserData.objects.exclude(id=user.id).filter(email=user.email).exists()
            )
            if existing_user:
                return Response(
                    {"email": ["Email already exists"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

           
            if password and confirm_password:
                if password != confirm_password:
                    return Response(
                        {"password": ["Passwords do not match"]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    user.set_password(password)

            user.save()
            return Response({"Success": "User Updated"}, status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class SubscriptionPriceViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPrice.objects.all()
    serializer_class = SubscriptionPriceSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        subscription_type = request.data.get('subscription_type')
        price = request.data.get('price')
        
        try:
            subscription_price = SubscriptionPrice.objects.get(subscription_type=subscription_type)
            subscription_price.price = price
            subscription_price.save()
            return Response(SubscriptionPriceSerializer(subscription_price).data, status=status.HTTP_200_OK)
        except SubscriptionPrice.DoesNotExist:
            return super().create(request, *args, **kwargs)

class Tasker_Listing(APIView):
    def get(self, request):
        users = UserData.objects.filter(is_staff=True,is_superuser = False)

        serializer = UserDataSerializer(users, many=True)
        return Response(serializer.data)
    
class Work_Listing(APIView):
    def get(self, request):
        task = WorkCategory.objects.all()
        serializer = WorkCategorySerializer(task, many=True)
        return Response(serializer.data)
    
class WorkCategoryAdding(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = WorkCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EditWorkCategory(APIView):
    parser_classes = (MultiPartParser, FormParser)
    

    def put(self, request, pk, *args, **kwargs):
        try:
            
            work_category = WorkCategory.objects.get(pk=pk)
        except WorkCategory.DoesNotExist:
            return Response({'error': 'Work category not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = WorkCategorySerializer(work_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class BlockWorkCategory(APIView):

    def post(self, request, pk, *args, **kwargs):
        try:
            work_category = WorkCategory.objects.get(pk=pk)
        except WorkCategory.DoesNotExist:
            return Response({'error': 'Work category not found'}, status=status.HTTP_404_NOT_FOUND)

        work_category.blocked = not work_category.blocked
        work_category.save()

        if work_category.blocked:
            message = 'Work category blocked successfully'
        else:
            message = 'Work category unblocked successfully'

        return Response({'status': message, 'blocked': work_category.blocked}, status=status.HTTP_200_OK)