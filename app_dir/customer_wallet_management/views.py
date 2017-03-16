from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.customer_wallet_management.serializers import CustomerWalletSerializer


class CustomerWalletView(generics.RetrieveUpdateDestroyAPIView):
    """
        This Api gets a wallet for a given customer
        HTTP method: GET
        URI: /wallet/retrieve_update/wallet_id

        wallet_id: :type(string) A UUID string as wallet identifier

        Expected Response:
        200: ok
        {
            "wallet_id": "8deda0f5-3555-4507-a0f6-04ea82954544",
            "msisdn": "254720317401",
            "token": "ec089d4a-483e-427a-87ab-091e9469e251",
            "name": "Ann",
            "status": "active",
            "type": "normal",
            "balance": 10000
        }
        """
    queryset = CustomerWallet.objects.all().order_by('-created_at')
    serializer_class = CustomerWalletSerializer
    permission_classes = (IsAdminUser,)
    lookup_field = 'wallet_id'


class CustomerWalletList(generics.ListCreateAPIView):
    """
        This Api creates a customer wallet object
        HTTP method: POST
        URI: /wallet/list_create

        Example payload:
        {
            {
                "wallet_id": "8deda0f5-3555-4507-a0f6-04ea82954544",
                "msisdn": "254720317401",
                "token": "ec089d4a-483e-427a-87ab-091e9469e251",
                "name": "Ann",
                "status": "active",
                "type": "normal",
                "balance": 10000
            }
        }

        wallet_id: :type(string) A UUID string as wallet identifier
        msisdn: :type(string) User's phone number
        token: :type(string) User's token
        name: :type(string) User's name
        status: :type(string) User status ["active", "dormant", "inactive"]
        type: :type(string) Type of the user ["normal", "merchant"]
        balance: :type(string) User's balance

        Expected Response:
        201: created
        """
    queryset = CustomerWallet.objects.all().order_by('-created_at')
    serializer_class = CustomerWalletSerializer
    permission_classes = (IsAdminUser,)
