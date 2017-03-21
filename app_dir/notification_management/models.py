import uuid

from django.db import models

from app_dir.customer_wallet_management.models import CustomerWallet


class Notification(models.Model):
    """
    This model defines the transaction notifications that go to the Customer.
    """

    NOTIFICATION_STATES = (
        ("pending", "pending"),
        ("in_progress", "in_progress"),
        ("success", "success"),
        ("failed", "failed")
    )

    NOTIFICATION_TYPES = (
        ("push", "push"),
        ("normal", "normal"),
    )
    notid = models.UUIDField(unique=True, default=uuid.uuid4)
    customer = models.ForeignKey(CustomerWallet)
    message = models.CharField(max_length=512, blank=True, default="")
    state = models.CharField(max_length=20,
                             choices=NOTIFICATION_STATES,
                             default="pending")
    notification_type = models.CharField(max_length=20,
                                         choices=NOTIFICATION_TYPES,
                                         )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{name}: {msisdn}".format(
                name=self.customer.name,
                msisdn=self.customer.msisdn
        )

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'


class NotificationDeviceMap(models.Model):
    """
    A model to map teams and devices to wallets
    """
    msisdn = models.CharField(max_length=20, null=True, blank=True)
    token = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    team_name = models.CharField(max_length=64, null=True, blank=True)
    user_type = models.CharField(max_length=20, null=True, blank=True)



