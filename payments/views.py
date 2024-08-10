from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = 'https://taskbridge-client.onrender.com/'  # Change to your domain
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': 'PRICE_ID',  # Replace with your actual price ID
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '?success=true',
                cancel_url=YOUR_DOMAIN + '?canceled=true',
            )
            return JsonResponse({'url': checkout_session.url})
        except stripe.error.StripeError as e:
            # Log Stripe error details
            print(f"Stripe Error: {e}")
            return JsonResponse({'error': f"Stripe Error: {str(e)}"}, status=500)
        except Exception as e:
            # Log general error details
            print(f"General Error: {e}")
            return JsonResponse({'error': f"General Error: {str(e)}"}, status=500)
