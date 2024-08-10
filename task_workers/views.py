from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from .models import Tasker, WorkCategory,SubscriptionPrice
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import json
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import JsonResponse
import stripe
from account.utils import send_admin_email
from rest_framework import status
from account.models import UserData
from django.conf import settings
from .serializers import TaskerSerializer, WorkCategorySerializer,TaskerFetchingSerializer,TaskerUpdateSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

@permission_classes([AllowAny])
class WorkCategoryListView(generics.ListAPIView):
    queryset = WorkCategory.objects.all()
    serializer_class = WorkCategorySerializer

@permission_classes([AllowAny])
class Work_Listing(APIView):
    def get(self, request):
        task = WorkCategory.objects.filter(blocked=False)
        serializer = WorkCategorySerializer(task, many=True)
        return Response(serializer.data)



class TaskerSignupView(generics.CreateAPIView):
    queryset = Tasker.objects.all()
    serializer_class = TaskerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        print('Request received for Tasker signup')

       
        print(f'Request user: {request.user}')
        print(f'User authenticated: {request.user.is_authenticated}')

        if not request.user.is_authenticated:
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        user = request.user

        # Optional: Ensure user is set to staff only if required by your logic
        user.requested_to_tasker = True
        admins = UserData.objects.filter(is_superuser=True)
        for admin in admins:
            send_admin_email(admin.email, user.name)
        user.save()

        # Print request data for debugging
        print(f'Request data: {request.data}')

        # Correct the request data
        corrected_data = request.data.copy()
        if 'task_service_charge' in corrected_data:
            corrected_data['task_fee'] = corrected_data.pop('task_service_charge')

        serializer = self.get_serializer(data=corrected_data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except Exception as e:
            print(f'Error during Tasker creation: {e}')
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Generate refresh and access tokens for the user
        refresh = RefreshToken.for_user(user)
        response_data = serializer.data
        response_data['refresh'] = str(refresh)
        response_data['access'] = str(refresh.access_token)

        # Add a flag to indicate the user needs to make a payment
        response_data['needs_payment'] = True

        return Response(response_data, status=status.HTTP_201_CREATED)


class PaymentOptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        monthly_price = SubscriptionPrice.objects.get(subscription_type=SubscriptionPrice.MONTHLY).price
        yearly_price = SubscriptionPrice.objects.get(subscription_type=SubscriptionPrice.YEARLY).price
        
        payment_options = {
            'monthly': {
                'price': monthly_price,
                'description': 'Monthly subscription'
            },
            'yearly': {
                'price': yearly_price,
                'description': 'Yearly subscription'
            }
        }
        return Response(payment_options)
    

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        subscription_type = request.data.get('subscription_type')
        if subscription_type not in [SubscriptionPrice.MONTHLY, SubscriptionPrice.YEARLY]:
            return JsonResponse({'error': 'Invalid subscription type'}, status=400)

        price_obj = SubscriptionPrice.objects.get(subscription_type=subscription_type)
        price_in_cents = int(price_obj.price * 100)

        try:
            frontend_base_url = "https://taskbridge-client.onrender.com"  # Your React app's base URL
            success_url = f"{frontend_base_url}/checkout_success?subscription_type={subscription_type}"
            cancel_url = f"{frontend_base_url}/checkout_cancel?subscription_type={subscription_type}"
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'inr',
                            'product_data': {
                                'name': f'{subscription_type.capitalize()} Subscription',
                            },
                            'unit_amount': price_in_cents,
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=request.user.id,
            )
            return JsonResponse({'url': checkout_session.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)








@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    
    def post(self, request, *args, **kwargs):

        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session.get('client_reference_id')

            if user_id:
                try:
                    user = UserData.objects.get(id=user_id)
                    user.is_staff = True
                    user.save()
                    # Update Tasker profile
                    tasker_profile = user.tasker_profile
                    tasker_profile.subscription_status = 'active'
                    tasker_profile.subscription_type = session['display_items'][0]['custom']['name'].lower()
                    tasker_profile.save()
                except UserData.DoesNotExist:
                    return JsonResponse({'error': 'User not found'}, status=400)

        return JsonResponse({'status': 'success'}, status=200)



class LogPaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_i = request.user
        subscription_type = request.data.get('subscription_type')

        try:
            # Update user
            user_i.is_staff = True
            user_i.payment_time = False
            user_i.save()

            # Update Tasker profile
            tasker_profile = Tasker.objects.get(user=user_i)
            tasker_profile.subscribed = True
            tasker_profile.subscription_type = subscription_type
            tasker_profile.activate_subscription()
        except Tasker.DoesNotExist:
            return JsonResponse({'error': 'Tasker profile not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        return JsonResponse({'status': 'success'}, status=200)


class LogPaymentCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return JsonResponse({'status': 'canceled'}, status=200)


    
class PaymentSuccessView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Payment successful!'})

class PaymentCancelView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Payment canceled.'})

    
    




class TaskerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = TaskerFetchingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        tasker = Tasker.objects.get(user=self.request.user)
        print(tasker)
        return tasker
    

class TaskerProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        try:
            tasker_profile = Tasker.objects.get(user=request.user)
        except Tasker.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskerUpdateSerializer(instance=tasker_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)