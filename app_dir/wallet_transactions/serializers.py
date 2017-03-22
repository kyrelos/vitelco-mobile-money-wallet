from rest_framework import serializers

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.models import Transaction, \
    BatchTransaction, BatchTransactionLookup, DebitMandate


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
        fields = ["trid", "source", "destination", "amount",
                  "transaction_type"]


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
        model = BatchTransaction
        fields = ["batch_trid", "merchant", "processing", "batch_title",
                  "batch_status"]


class BatchTransactionLookUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = BatchTransactionLookup
        fields = ["batch_transaction_id", "transaction_id"]


class DebitMandateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DebitMandate
        fields = ["currency", "amount_limit", "start_date", "end_date",
                  "frequency_type", "mandate_status", "request_date",
                  "number_of_payments", "account_id"]

