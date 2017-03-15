from rest_framework import serializers

from app_dir.customer_wallet_management.models import CustomerWallet
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    This is a serializer for the ListCcreateNotification view. Its is
    configured to use customers wallet_id instead of primary keys for
    lookup and creating the customer wallet object.
    The main reason for this is that wallet_id will be more consistent
    compared to primary key.
    """
    customer = serializers.SlugRelatedField(
            many=False,
            read_only=False,
            slug_field='wallet_id',
            queryset=CustomerWallet.objects.all()
    )

    class Meta:
        model = Notification
        fields = ["customer", "notid", "message", "type"]
