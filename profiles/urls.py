from django.urls import path

from .views import GetProfileAPIView, UpdateProfileAPIView

urlpatterns = [
    path("me/", GetProfileAPIView.as_view(), name="get_profile"),
    path("update/", UpdateProfileAPIView.as_view(), name="update_profile")
]
