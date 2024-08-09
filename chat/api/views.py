from .serializer import ChatSerializer , EmployeeChatSerializer, UserChatSeralizer
from rest_framework.generics import ListAPIView , RetrieveUpdateDestroyAPIView
from chat.models import Chat
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework import status
from account.models import UserData
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile



@permission_classes([IsAuthenticated])
class GetMessage(ListAPIView):
    serializer_class = ChatSerializer
    def get_queryset(self):
        sender_id = self.kwargs['sender_id']
        reciever_id = self.kwargs['reciever_id']
        queryset = Chat.objects.filter(
            sender__in=[sender_id, reciever_id],
            receiver__in=[sender_id, reciever_id]
        ).order_by('date')
        for message in queryset:
            if message.receiver.id == self.request.user.id:
                message.is_read = True
                message.save()

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@permission_classes([IsAuthenticated])
class GetEmployeeMessage(ListAPIView):
    serializer_class =EmployeeChatSerializer
    def get(self, request, *args, **kwargs):
        employee_id = self.kwargs['pk']
        dic = {}
        employee_chat = Chat.objects.filter(receiver__in = [employee_id])
        for chat in employee_chat:
            sender_id = chat.sender.id 
            sender_first_name = chat.sender.first_name
            sender_last_name = chat.sender.last_name
            sender_images = chat.sender.images if chat.sender.images else None
            if sender_id not in dic:
                dic[sender_id] = {
                    'id':sender_id,
                    'first_name':sender_first_name,
                    'last_name':sender_last_name,
                    'images':sender_images
                }
        data_list = list(dic.values())
        serializer  = self.serializer_class(data=data_list,many=True)
        try:
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except serializers.ValidationError as e:
            return Response({"message": "serializer is not valid", "errors": e.detail})


@permission_classes([IsAuthenticated])
class GetUsersChatWithTasker(ListAPIView):
    serializer_class = UserChatSeralizer

    def get_queryset(self):
        tasker_id = self.kwargs['tasker_id']
        # Get the latest chat messages by date for each sender
        latest_chats = (
            Chat.objects.filter(receiver_id=tasker_id)
            .order_by('sender', '-date')
            .distinct('sender')
        )

        # Extract the sender ids from the latest chat messages
        sender_ids = latest_chats.values_list('sender_id', flat=True)

        # Get the users corresponding to the sender ids
        users = UserData.objects.filter(id__in=sender_ids)

        return users

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendMessage(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        sender_id = request.data.get('sender')
        receiver_id = request.data.get('receiver')
        image = request.FILES.get('image')
    

        if not sender_id or not receiver_id:
            return Response({"error": "Sender and receiver are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = UserData.objects.get(id=sender_id)
            receiver = UserData.objects.get(id=receiver_id)
        except UserData.DoesNotExist:
            return Response({"error": "Invalid sender or receiver"}, status=status.HTTP_400_BAD_REQUEST)

        chat = Chat(sender=sender, receiver=receiver, message=message)

        if image:
            # Save the image and get its URL
            image_name = default_storage.save(f'chat_images/{image.name}', ContentFile(image.read()))
            image_url = default_storage.url(image_name)
            chat.image = image_url

            chat.save()

        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)