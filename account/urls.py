from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import( RegisterView, HomeView, LogoutView, LoginView,
                    VerifyOTP,ResendOtpView,Tasker_ListingView,
                    TaskCategory_ListingView,Category_Tasker_filter,
                    SearchTasker,TaskerDetails,UserIndivualView,test_view,
                    BestTaskers,Adds_Taskers,Service_Taskers,ReportToAdmin)

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='api-login'),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="sign_up"),
    path('api/validate-otp', VerifyOTP.as_view(), name='validate_otp'),
    path('api/resend-otp', ResendOtpView.as_view(), name='resend_otp'),
    path("api/home/", HomeView.as_view(), name="home"),
    path("api/taskcategory/", TaskCategory_ListingView.as_view(), name="home"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path("api/taskers/", Tasker_ListingView.as_view(), name="taskers"),
    path('api/bestTasker/', BestTaskers.as_view(), name='best-tasker'),
    path('api/addsTasker/', Adds_Taskers.as_view(), name='adds-tasker'),
    path('api/serviceTasker/', Service_Taskers.as_view(), name='service-tasker'),
    path("api/tasker_filter/<int:taskId>/", Category_Tasker_filter.as_view(), name="tasker_filter"),
    path("api/search_tasker/", SearchTasker.as_view(), name="search_tasker"),
    path('report-worker/<int:user_id>/', ReportToAdmin.as_view(), name='report-worker'),
    path('api/tasker-details/<int:user_id>/', TaskerDetails.as_view(), name='tasker-details'),
    path("api/userindivual/<int:pk>/", UserIndivualView.as_view(),name='token_refersh'),



    path('test-endpoint/', test_view, name='test_view'),

]
