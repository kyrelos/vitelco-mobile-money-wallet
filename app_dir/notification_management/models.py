from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class Notification(models.Model):
    """
    This model defines the transaction notifications that go to the Customer.
    """

    NOTIFICATION_STATES = (
        ("pending", "pending"),
        ("success", "success"),
        ("failed", "failed")
    )

    NOTIFICATION_TYPES = (
        ("push", "push"),
        ("transaction_message", "transaction_message"),
    )
    notid = models.UUIDField(unique=True)
    customer = models.ForeignKey(CustomerWallet)
    message = models.CharField(max_length=512, blank=True, default="")
    state = models.CharField(max_length=20,
                             choices=NOTIFICATION_STATES,
                             default="pending")
    type = models.CharField(max_length=20,
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

