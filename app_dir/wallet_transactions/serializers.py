from rest_framework import serializers

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    This is a serializer for the CreateNotification view.
    """

    source = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='wallet_id',
        queryset=CustomerWallet.objects.all()
    )

    destination = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='wallet_id',
        queryset=CustomerWallet.objects.all()
    )

    class Meta:
        model = Transaction
        fields = ["trid", "source", "destination", "amount", "type"]


class BatchTransactionSerializer(serializers.ModelSerializer):
    """
    This is a serializer for the CreateNotification view.
    """

    merchant = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        slug_field='wallet_id',
        queryset=CustomerWallet.objects.all()
    )

    class Meta:
        model = Transaction
        fields = ["batch_trid", "merchant", "processing", "batch_title",
                  "batch_status"]

