from rest_framework import generics, permissions
from booking.models import Appointment
from .serializers import AppointmentSerializer
from rest_framework.response import Response
from rest_framework import status
from django.views import View
from task_workers.models import Tasker
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from account.utils import send_tasker_email
from django.core.exceptions import PermissionDenied
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from account.utils import generate_otp,send_otp_email
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from account.utils import send_user_appointment_email


class CreateAppointmentAPIView(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print("Incoming data:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Retrieve user and employee emails
        appointment = serializer.instance
        user = appointment.user
        employee_email = appointment.employee.email
        print(employee_email)
        send_tasker_email(employee_email, user)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UpdateAppointmentAPIView(generics.UpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        print("Incoming data for update:", request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_update(serializer)

        appointment = serializer.instance
        user = appointment.user
        employee_email = appointment.employee.email
        print("Updated employee email:", employee_email)
        

        send_tasker_email(employee_email, user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        serializer.save()

class CancelAppointmentAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        appointment_id = kwargs.get('appointment_id')
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if appointment.status == 'canceled':
                return Response({"detail": "Appointment is already canceled."}, status=status.HTTP_400_BAD_REQUEST)
            
            appointment.status = 'canceled'
            appointment.save()

            # Send notification emails
            user = appointment.user
            employee_email = appointment.employee.email
            print("Canceled employee email:", employee_email)
            send_tasker_email(employee_email, user)

            return Response({"detail": "Appointment canceled successfully."}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)


class AppointmentHistory(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        tasker_id = self.request.query_params.get('tasker_id')
        now = timezone.now()

        appointments = Appointment.objects.filter( date__lt=now,status='pending')
        for appointment in appointments:
            appointment.status = 'canceled'
            appointment.save() 
        
        if not tasker_id:
            raise ValidationError("Tasker ID is required")
        return Appointment.objects.filter(user=user, employee__id=tasker_id)


    

class TaskerAppointmentHistoryView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        appointments = Appointment.objects.filter(employee=user, date__lt=now, status='pending')
        for appointment in appointments:
            appointment.status = 'canceled'
            appointment.save() 

        return Appointment.objects.filter(employee=user).order_by('date')
    

class TodayTomorrowAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        tomorrow = today + timezone.timedelta(days=1)

        today_appointments = Appointment.objects.filter(employee=user, date=today)
        tomorrow_appointments = Appointment.objects.filter(employee=user, date=tomorrow)

        today_serializer = AppointmentSerializer(today_appointments, many=True)
        tomorrow_serializer = AppointmentSerializer(tomorrow_appointments, many=True)

        return Response({
            'today': today_serializer.data,
            'tomorrow': tomorrow_serializer.data
        })
    
class ManagingAppointment:
    def __init__(self, tasker):
        self.tasker = tasker

    def accept_appointment(self, appointment, email, info):
        if appointment.employee != self.tasker:
            raise PermissionDenied("You do not have permission to accept this appointment.")
        appointment.status = Appointment.ACCEPTED
        appointment.save()
        send_user_appointment_email(email, 'accepted', info)
        return appointment

    def reject_appointment(self, appointment, email, info):
        if appointment.employee != self.tasker:
            raise PermissionDenied("You do not have permission to reject this appointment.")
        appointment.status = Appointment.REJECTED
        appointment.save()
        send_user_appointment_email(email, 'rejected', info)
        return appointment
    
class CompleteAppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            if appointment.employee != request.user:
                return Response({"detail": "You do not have permission to complete this appointment."}, 
                                status=status.HTTP_403_FORBIDDEN)

            otp = generate_otp()
            print(otp)
            appointment.otp = otp
            appointment.otp_time = timezone.now()
            appointment.save()

            send_otp_email(appointment.user.email, otp)

            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
        
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)


class VerifyOTP(APIView):
    def post(self, request, appointment_id):
        otp_entered = request.data.get('otp')
        print(f"OTP entered: {otp_entered}, Appointment ID: {appointment_id}")
        
        if not otp_entered:
            return Response({'detail': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            if appointment.otp != otp_entered:
                return Response({'detail': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
            
            if appointment.otp_time:
                current_time = timezone.now()
                otp_time = appointment.otp_time

                # Check if the OTP is within 1 minute
                if current_time - otp_time > timedelta(minutes=1):
                    return Response({'detail': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)

            appointment.status = 'complete'
            appointment.otp = None
            appointment.otp_time = None
            appointment.save()
            employee = Tasker.objects.get(user=appointment.employee)
            employee.rating+=1
            employee.save()


            return Response({'message': 'Task completed successfully.'}, 
                            status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({'detail': 'Appointment not found'}, status=status.HTTP_404_NOT_FOUND)


class ManageAppointmentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, appointment_id, new_status):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if new_status not in [Appointment.PENDING, Appointment.ACCEPTED, Appointment.REJECTED]:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
                
            appointment.status = new_status
            info_data = request.data
            info = info_data.get('info', '')
            if info_data: 
                appointment.rejection_reason = info
            if new_status == 'accepted':
                info='Congratulations! your appointment is accepted'+' ' + info
            elif new_status == 'rejected':
                info='Sorry! your appointment is rejected' + ' ' + info
            
            send_user_appointment_email(appointment.user.email, 'rejected', info)
            appointment.save()
            return Response({"status": "success", "new_status": new_status}, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
