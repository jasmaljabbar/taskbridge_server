from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer,LoginSerializer,TaskerHomeSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .utils import generate_otp, report_admin,send_otp_email
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from rest_framework.decorators import permission_classes
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.permissions import AllowAny
from datetime import timedelta
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from .models import UserData
from rest_framework_simplejwt.views import TokenObtainPairView
from task_workers.models import Tasker
from task_workers.models import WorkCategory
from task_workers.serializers import WorkCategorySerializer,TaskerFetchingSerializer






@permission_classes([AllowAny])
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    

@permission_classes([AllowAny])
class VerifyOTP(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp_entered = request.data.get('otp')

        try:
            user = UserData.objects.get(email=email, otp=otp_entered)
            print('email:',email, 'otp:',otp_entered)
            if user.otp_time:
                current_time = timezone.now()
                otp_time = user.otp_time

                # Check if the OTP is within 1 minutes
                if current_time - otp_time > timedelta(minutes=1):
                    return Response({'detail': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.otp = None
            user.otp_time = None
            user.save()


            return Response({'message': 'Email verified successfully.'}, 
                              status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAuthenticated])
class UserIndivualView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = UserData.objects.all()


@permission_classes([AllowAny])
class RegisterView(APIView):
     def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            otp = generate_otp()
            user.otp = otp
            user.otp_time = timezone.now()
            print(otp)
            user.save()

            send_otp_email(user.email, otp)

            return Response({'message': 'User registered successfully. OTP sent to your email.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([AllowAny])    
class ResendOtpView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = UserData.objects.get(email=email)

            otp = generate_otp()
            user.otp = otp
            user.otp_time = timezone.now()
            print(otp)
            user.save()

            send_otp_email(user.email, otp)

            return Response({'message': 'New OTP sent to your email.'}, status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    

class HomeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        user_info = {
            "username": user.name,
            "email": user.email,
        }
        content = {"user": user_info}
        return Response(content)

@permission_classes([AllowAny])
class Tasker_ListingView(APIView):
    def get(self, request):
        taskers = Tasker.objects.filter(
            Q(subscribed=True) & Q(user__blocked_for_tasker=False)
        )[:9]
        serializer = TaskerHomeSerializer(taskers, many=True)
        return Response(serializer.data)


@permission_classes([AllowAny])
class BestTaskers(APIView):
    def get(self, request):
        taskers = Tasker.objects.filter(Q(rating__gt=0) & Q(subscribed=True) & Q(user__blocked_for_tasker=False)).order_by('-rating')[:3]
        serializer = TaskerHomeSerializer(taskers, many=True)
        return Response(serializer.data)
    

@permission_classes([AllowAny])
class Adds_Taskers(APIView):
    def get(self, request):
        taskers = Tasker.objects.filter(rating__gt=0).order_by('-rating')[4:7]
        serializer = TaskerHomeSerializer(taskers, many=True)
        return Response(serializer.data)



@permission_classes([AllowAny])
class Service_Taskers(APIView):
    def get(self, request):
        taskers = Tasker.objects.filter(rating__gt=0).order_by('-rating')[7:9]
        serializer = TaskerHomeSerializer(taskers, many=True)
        return Response(serializer.data)



@permission_classes([AllowAny])
class TaskCategory_ListingView(APIView):
    def get(self,request):
        taskCategoty = WorkCategory.objects.all()
        serializer = WorkCategorySerializer(taskCategoty, many=True)
        return Response(serializer.data)
    
    
@permission_classes([AllowAny])
class Category_Tasker_filter(APIView):
    def get(self, request, taskId, *args, **kwargs):
        try:
            workCategory = WorkCategory.objects.get(id=taskId)
            taskers = Tasker.objects.filter(Q(task=workCategory) & Q(subscribed=True) & Q(user__blocked_for_tasker=False))
            serializer = TaskerHomeSerializer(taskers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except WorkCategory.DoesNotExist:
            return Response({"error": "Work category not found"}, status=status.HTTP_404_NOT_FOUND)
        
@permission_classes([AllowAny])
class SearchTasker(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')
        taskers = Tasker.objects.filter(
            Q(full_name__icontains=query)& Q(subscribed=True) & Q(user__blocked_for_tasker=False) | Q(task__name__icontains=query)
            & Q(subscribed=True) & Q(user__blocked_for_tasker=False)
        )
        
        serializer = TaskerHomeSerializer(taskers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    

class TaskerDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        try:
            tasker = Tasker.objects.get(user__id=user_id)
            serializer = TaskerFetchingSerializer(tasker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Tasker.DoesNotExist:
            return Response({"error": "Tasker not found"}, status=status.HTTP_404_NOT_FOUND)
        

class ReportToAdmin(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:

            worker = UserData.objects.get(id=user_id)

   
            reporter = request.user
            
            admin_emails = UserData.objects.filter(is_superuser=True).values_list('email', flat=True)

            if not admin_emails:
                return Response({"detail": "No admin emails found."}, status=status.HTTP_404_NOT_FOUND)

            subject = f"Report about Worker {worker.username}"
            message = (
                f"User {reporter.username} has reported about the worker {worker.username}.\n\n"
                "Please check the details in the admin panel."
            )
            

            for admin in admin_emails:
                # Send the email
                report_admin(admin, message,subject)


            return Response({"detail": "Report sent successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "Worker not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = self.user
        subscriptionValidation(user)
        try:
            refresh_token = request.data.get("refreshToken")
            if refresh_token:
                RefreshToken(refresh_token).blacklist()
                return Response(status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)






# account/views.py
from django.http import JsonResponse

def test_view(request):
    return JsonResponse({'message': 'This is a test endpoint.'})
