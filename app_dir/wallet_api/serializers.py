from rest_framework import serializers
from app_dir.wallet_transactions.models import Transaction

class TransactionSerializer(serializers.Serializer):
    class Meta:
        model = Transaction
        fields = ["trid", "source", "destination", "amount", "type"]

