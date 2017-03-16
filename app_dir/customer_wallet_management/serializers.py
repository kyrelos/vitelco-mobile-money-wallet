from rest_framework import serializers
from .models import CustomerWallet


class CustomerWalletSerializer(serializers.ModelSerializer):
    """
    This is a serializer for the CustomerWallet view.
    """

    class Meta:
        model = CustomerWallet
        fields = ('wallet_id', 'msisdn', 'token', 'name', 'status', 'type', 'balance')
