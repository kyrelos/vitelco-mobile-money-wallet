from rest_framework import serializers

from app_dir.customer_wallet_management.models import CustomerWallet
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    customer = serializers.SlugRelatedField(
            many=False,
            read_only=False,
            slug_field='wallet_id',
            queryset=CustomerWallet.objects.all()
    )

    class Meta:
        model = Notification
        fields = ["customer", "notid", "message", "type"]
