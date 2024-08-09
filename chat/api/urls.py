from django.urls import path
from .views import GetMessage , GetEmployeeMessage, GetUsersChatWithTasker,SendMessage

urlpatterns = [  
    path('message/<int:sender_id>/<int:reciever_id>/', GetMessage.as_view(), name='text-message'),
    path('employeemessage/<int:pk>/', GetEmployeeMessage.as_view(), name='employee-messsage'),
    path('users-chat-with-tasker/<int:tasker_id>/', GetUsersChatWithTasker.as_view(), name='users-chat-with-tasker'),
    path('send_message/', SendMessage.as_view(), name='send-message'),
]
