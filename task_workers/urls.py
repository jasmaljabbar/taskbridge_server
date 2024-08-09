from django.urls import path
from .views import (TaskerSignupView,TaskerProfileView,
                    TaskerProfileUpdateView,Work_Listing,
                    PaymentOptionsView,CreateCheckoutSessionView,
                    StripeWebhookView,PaymentCancelView,
                    PaymentSuccessView,LogPaymentCancelView,LogPaymentSuccessView
)
urlpatterns = [
    path('become_tasker/', TaskerSignupView.as_view(), name='tasker_signup'),
    path('payment/options/', PaymentOptionsView.as_view(), name='payment-options'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('payment/success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('payment/log_success/', LogPaymentSuccessView.as_view(), name='log-payment-success'),
    path('payment/log_cancel/', LogPaymentCancelView.as_view(), name='log-payment-cancel'),
    path('profile/', TaskerProfileView.as_view(), name='tasker-profile'),
    path('TaskerProfile/', TaskerProfileView.as_view(), name='tasker-profile'),
    path('update/', TaskerProfileUpdateView.as_view(), name='tasker-profile-update'),
    path('workcategory/', Work_Listing.as_view(), name='tasker-profile-update'),
]
