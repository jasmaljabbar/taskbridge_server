from django.urls import path
from .views import (
    CreateAppointmentAPIView,
    AppointmentHistory,
    TaskerAppointmentHistoryView,
    ManageAppointmentStatusView,
    UpdateAppointmentAPIView,
    CancelAppointmentAPIView,
    VerifyOTP,
    CompleteAppointmentAPIView,
    TodayTomorrowAppointmentsView,
)

urlpatterns = [
    path('appointments/', CreateAppointmentAPIView.as_view(), name='appointment-create'),
    path('appointment/history/', AppointmentHistory.as_view(), name='appointment-history'),
    path('appointment/taskerHistory/', TaskerAppointmentHistoryView.as_view(), name='appointmentTasker-history'),
    path('appointment/manage/<int:appointment_id>/<str:new_status>/', ManageAppointmentStatusView.as_view(), name='manage_appointment_status'),
    path('appointment/update/<int:pk>/', UpdateAppointmentAPIView.as_view(), name='appointment-update'),
    path('appointment/cancel/<int:appointment_id>/', CancelAppointmentAPIView.as_view(), name='appointment-cancel'),
    path('verify-otp/<int:appointment_id>/', VerifyOTP.as_view(), name='verify_otp'),
    path('today-tomorrow/', TodayTomorrowAppointmentsView.as_view(), name='today-tomorrow-appointments'),
    path('appointment/complete/<int:appointment_id>/', CompleteAppointmentAPIView.as_view(), name='complete_appointment'),

]
