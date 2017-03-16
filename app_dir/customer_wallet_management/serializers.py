from rest_framework import serializers
from .models import CustomerWallet

class CustomerWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerWallet
        fields = ('wallet_id', 'msisdn', 'token', 'name', 'status', 'type', 'balance', 'created_at', 'modified_at')
