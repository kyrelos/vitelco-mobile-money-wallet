from rest_framework import generics
from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.permissions import IsAdminUser


class TransactionCreateList(generics.ListCreateAPIView):
    """
    This Api creates a transaction object for a single transaction
    HTTP method: POST
    URI: /transactions/list_create

    Example payload:
    {
        "trid": "24f6654c-9e76-419d-a55a-cb6ab520af4c",
        "source": "d4664ed6-0a39-11e7-b188-c7bc39d6527f",
        "destination": "153b8e3e-0a3b-11e7-8880-3f4930b3363a",
        "type": "deposit",
        "amount": "100"
    }


    trid: :type(string) A UUID string as transaction id
    source: :type(string) A UUID string representing the customers wallet_id
    destination: :type(string) A UUID string representing the customers
     wallet_id
    type: :type(string) Type of the message
     ["reversal", "payment", "deposit", "withdrawal", "p2p"]
    amount: :type(integer) an integer represent the amount of money

    Expected Response:
    Expected Response:
    201: created
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAdminUser,)
