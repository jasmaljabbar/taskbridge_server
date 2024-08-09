from django.urls import path 
from .views import *


urlpatterns = [
    path('UserProfileDetailView/<int:pk>/', UserIndvualViewPermsion.as_view(), name='user-profile-detail'),
    path('employeeindividualPermission/<int:pk>/', EmployeesIndvualViewPermsion.as_view(), name='employee-list'),
    path('counts/', UserWorkerCountView.as_view(), name='user-worker-counts'),
    path('subscription_income/', SubscriptionIncomeDashboard.as_view(), name='subscription-income-dashboard'),
    path('subscriptions/', TaskerSubscriptionView.as_view(), name='tasker-subscriptions'),
    path('user_distribution/', UserDistributionView.as_view(), name='user_distribution'),
    path('user_growth/', UserGrowthView.as_view(), name='user_growth'),
    path('accepted-appointments/', CompletedAppointmentsView.as_view(), name='accepted-appointments'),
     path('download_report/', DownloadReportView.as_view(), name='download_report'),
]