from django.shortcuts import render
from rest_framework import generics , status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser , IsAuthenticated , AllowAny
from . serializer import EmployeeIndvualSerializers,UserIndvualSerializers,CountSerializer,TaskerSubscriptionSerializer,BookingAppointmentSerializer
from task_workers.models import Tasker
from rest_framework.response import Response
from account.models import UserData
from django.conf import settings
from django.contrib.auth import get_user_model
from . models import SubscriptionIncome
from django.utils import timezone
from datetime import timedelta
from profiles.models import Profile
from task_workers.models import Tasker,SubscriptionPrice 
from task_workers.serializers import TaskerSerializer
from rest_framework.views import APIView
from booking.models import Appointment
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum, F
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
import csv
from django.http import HttpResponse





@permission_classes([IsAuthenticated])
class EmployeesIndvualViewPermsion(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EmployeeIndvualSerializers
    def get_queryset(self):
        return Tasker.objects.filter(user__is_staff=True)  



class UserIndvualViewPermsion(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserIndvualSerializers
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.queryset.get(user__id=self.kwargs['pk'])


class UserWorkerCountView(APIView):
    permission_classes = [IsAuthenticated]  # Adjust the permissions as needed

    def get(self, request, *args, **kwargs):
        users_count = UserData.objects.count()
        workers_count = Tasker.objects.count()
        data = {
            'users_count': users_count,
            'workers_count': workers_count
        }
        serializer = CountSerializer(data=data)
        serializer.is_valid()  # You might need this to ensure data is valid
        return Response(serializer.data)
    


class Worker_mothely_subscribed(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        worker_monthly_subscribe = Tasker.objects.filter(subscribed=True, subscription_type='monthly')
        serializer = TaskerSerializer(worker_monthly_subscribe, many=True)
        return Response(serializer.data)
    


class SubscriptionIncomeDashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        income = SubscriptionIncome.objects.first()
        if not income:
            income = SubscriptionIncome.objects.create()

        data = {
            'monthly_subscription_income': income.monthly_subscription_income,
            'yearly_subscription_income': income.yearly_subscription_income,
        }
        print(data)
        return Response(data)


class TaskerSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        subscriptions = Tasker.objects.filter(subscribed=True)
        serializer = TaskerSubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)
    


User = get_user_model()

class UserDistributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        taskers = Tasker.objects.count()
        regular_users = total_users - taskers

        data = {
            'regular_users': regular_users,
            'taskers': taskers
        }
        return Response(data)

class UserGrowthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_growth = UserData.objects.annotate(
            month=TruncMonth('date_joined')
        ).values('month').annotate(
            users=Count('id')
        ).order_by('month')

        data = [
            {
                'date': entry['month'].strftime('%Y-%m-%d'),
                'users': entry['users']
            }
            for entry in user_growth
        ]
        return Response(data)




class CompletedAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        worker = request.user
        completed_appointments = Appointment.objects.filter(employee=worker, status=Appointment.COMPLETE)
        # Group by day with user
        daily_data = completed_appointments.annotate(day=TruncDay('date'), user_name=F('user__name')).values('day', 'user_name').annotate(
            total_hours=Sum('minimum_hours_to_work')).order_by('day')
        # Group by month with user
        monthly_data = completed_appointments.annotate(month=TruncMonth('date'), user_name=F('user__name')).values('month', 'user_name').annotate(
            total_hours=Sum('minimum_hours_to_work')).order_by('month')

        # Group by year with user
        yearly_data = completed_appointments.annotate(year=TruncYear('date'), user_name=F('user__name')).values('year', 'user_name').annotate(
            total_hours=Sum('minimum_hours_to_work')).order_by('year')

        return Response({
            'daily': list(daily_data),
            'monthly': list(monthly_data),
            'yearly': list(yearly_data),
        })




class DownloadReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with the appropriate CSV header.
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="sales_report.csv"'},
        )

        writer = csv.writer(response)
        writer.writerow(['Full Name', 'Subscription Start Date', 'Subscription Type', 'Subscription Price'])

        # Fetch the subscribed Tasker data
        subscribed_taskers = Tasker.objects.filter(subscribed=True).select_related('user')

        for tasker in subscribed_taskers:
            subscription_price = SubscriptionPrice.objects.get(subscription_type=tasker.subscription_type).price
            writer.writerow([
                tasker.full_name,
                tasker.formatted_subscription_start_date,
                tasker.subscription_type,
                subscription_price,
            ])

        return response