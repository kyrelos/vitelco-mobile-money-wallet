from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app_dir.notification_management.tasks import send_normal_notification
from app_dir.wallet_transactions.models import Transaction
from .models import Notification, NotificationDeviceMap
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
    permission_classes = (IsAdminUser, )


class UpdateNotification(APIView):
    """
    This API updates notification objects and Device attributes
    HTTP method: POST
    URI: /notification/update

    Example payload:
    {
        "request_type": ["token_refresh", "push_response"]
        "notification_id": "24f6654c-9e76-419d-a55a-cb6ab520af4c",
        "transaction_id": "24f6654c-9e76-419d-a55a-cb6ab520af4b",
        "token": "24f6654c-9e76-419d-a55a-cb6ab520af4b24f6654c-9e76-419d-a55a-cb6ab520af4b"
        "pin": "push",
        "msisdn": "msisdn",
        "status": ["accepted", "rejected"]
        "name": "name",
        "team_name": "team_name"
    }


    """

    def post(self, request):
        request_data = request.data
        request_type = request_data.get("request_type")

        try:
            if request_type == "token_refresh":
                msisdn = request_data["msisdn"]
                token = request_data["token"]
                name = request_data.get("name")
                team_name = request_data.get("team_name")
                device, created = NotificationDeviceMap.objects.get_or_create(
                        msisdn=msisdn)
                device.token = token
                device.name = name
                device.team_name = team_name
                device.save()
                response = Response(status=status.HTTP_200_OK)
                return response

            else:
                notification_id = request_data['notification_id']

                transaction_id = request_data['transaction_id']

                pin = request_data['pin']
                push_status = request_data['status']
                if str(pin) == "1234":
                    transaction = Transaction.objects.get(
                        trid=transaction_id)
                    transaction.complete_transaction()
                    transaction.save()
                    send_normal_notification.delay(notification_id,
                                                   transaction_id)

                response = Response(status=status.HTTP_200_OK)
                return response
        except KeyError as e:
            response = Response(
                    data={"exception": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
            )
            return response


