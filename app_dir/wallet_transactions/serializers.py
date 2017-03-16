from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('trid', 'source', 'destination', 'amount', 'type', 'state', 'created_at', 'modified_at')


