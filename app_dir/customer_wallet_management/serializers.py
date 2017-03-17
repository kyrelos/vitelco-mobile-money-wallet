from rest_framework import serializers


from .models import CustomerWallet


class CustomerWalletSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CustomerWallet
        fields = ("id", "msisdn", "balance", "type", "status")


class CustomerWalletStatusSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = CustomerWallet
        fields = ("msisdn", "status")
