from rest_framework import generics
from .models import Notification
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAdminUser


class NotificationList(generics.ListCreateAPIView):
    """
    This Api creates a notification object for a given customer
    HTTP method: POST
    URI: /notification/list_create

    Example payload:
    {
        "notid": "24f6654c-9e76-419d-a55a-cb6ab520af4c",
        "message": "Please verify payment of Ksh 1000 to Dominos",
        "type": "push",
        "customer": "24f6654c-9e76-419d-a55a-cb6ab520af4b"
    }


    notid: :type(string) A UUID string as notification identifier
    message: :type(string) Message to be displayed to the user
    type: :type(string) Type of the message ["transaction_message", "push"]
    customer: :type(string) A UUID string representing the customers wallet_id

    Expected Response:
    201: created
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAdminUser,)