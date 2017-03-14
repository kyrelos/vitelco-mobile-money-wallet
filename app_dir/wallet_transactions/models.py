from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class Transaction(models.Model):
    """
    This model defines a transaction, i.e. Movement of cash from one wallet_transactions
    to another
    """

    TRANSACTION_STATES = (
        ("received", "received"),
        ("in_progress", "in_progress"),
        ("completed", "completed")
    )

    TRANSACTION_TYPES = (
        ("reversal", "reversal"),
        ("payment", "payment"),
        ("deposit", "deposit"),
        ("withdrawal", "withdrawal"),
        ("statement", "statement"),
        ("p2p", "p2p")
    )
    transaction_id = models.UUIDField(primary_key=True, unique=True)
    source = models.ForeignKey(
            CustomerWallet,
            related_name="tansaction_source"
    )
    destination = models.ForeignKey(
            CustomerWallet,
            related_name="tansaction_destination"
    )
    amount = models.IntegerField()
    type = models.CharField(max_length=20,
                            choices=TRANSACTION_TYPES,
                            )

    state = models.CharField(max_length=20,
                             choices=TRANSACTION_STATES,
                             default="received"
                             )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{name}: {msisdn}".format(
                name=self.customer.name,
                msisdn=self.customer.msisdn
        )

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'


class BulkTransaction(models.Model):
    bulk_transaction_id = models.UUIDField(primary_key=True, unique=True)
    merchant = models.ForeignKey(
            CustomerWallet
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{name}: {msisdn}".format(
                name=self.merchant.name,
                msisdn=self.merchant.msisdn
        )

    class Meta:
        verbose_name = 'Bulk Transaction'
        verbose_name_plural = 'Bulk Transactions'




