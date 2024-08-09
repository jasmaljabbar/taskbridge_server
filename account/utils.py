

import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_otp(length=6):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

def send_otp_email(email, otp):
    subject = 'Your OTP for Login'
    message = f'Your OTP is: {otp}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def send_admin_email(email, user):
    subject = 'Tasker Request'
    message = f'Tasker requested by {user}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

def report_admin(email, message,subject):
    subject = subject
    message = message
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def send_tasker_email(email,user):
    subject = 'User Request'
    message = f'Booking requested by {user}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)


def send_user_appointment_email(email,sub,info):
    subject = f'Your Appintment {sub}'
    message = info
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)

