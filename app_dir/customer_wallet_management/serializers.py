from rest_framework import serializers


from .models import CustomerWallet


class CustomerWalletSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CustomerWallet
        fields = ("wallet_id", "msisdn", "balance", "type", "status")
