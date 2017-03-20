import uuid

from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class Transaction(models.Model):
    """
    This model defines a transaction, i.e. Movement of cash from one wallet
    to another
    """

    TRANSACTION_STATES = (
        ("pending", "pending"),
        ("in_progress", "in_progress"),
        ("completed", "completed"),
        ("failed", "failed")
    )

    TRANSACTION_TYPES = (
        ("reversal", "reversal"),
        ("payment", "payment"),
        ("deposit", "deposit"),
        ("transfer", "transfer"),
        ("withdrawal", "withdrawal"),
        ("statement", "statement"),
        ("p2p", "p2p")
    )
    trid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    currency = models.CharField(max_length=10, default="KES")
    source = models.ForeignKey(
            CustomerWallet,
            related_name="transaction_source"
    )
    destination = models.ForeignKey(
            CustomerWallet,
            related_name="transaction_destination"
    )
    amount = models.IntegerField()
    server_correlation_id = models.UUIDField(unique=True)
    transaction_type = models.CharField(max_length=20,
                                        choices=TRANSACTION_TYPES,
                                        )
    callback_url = models.URLField(null=True)

    state = models.CharField(max_length=20,
                             choices=TRANSACTION_STATES,
                             default="pending"
                             )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{source}: {destination}".format(
                source=self.source,
                destination=self.destination
        )

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'


class BatchTransaction(models.Model):
    """
    This model defines a Bulk transaction, i.e. Movement of cash from one
    wallet to multiple wallets
    to another
    """
    BATCH_STATUS = (
        ("created", "created"),
        ("finished", "finished"),
    )

    batch_trid = models.UUIDField(unique=True, default=uuid.uuid4)
    merchant = models.ForeignKey(
            CustomerWallet
    )
    processing = models.BooleanField(default=False)
    batch_title = models.TextField(null=False, default="BATCHTRX")
    batch_status = models.CharField(choices=BATCH_STATUS, max_length=20,
                                    default="created")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{name}: {msisdn} {batch_trid}".format(
                name=self.merchant.name,
                msisdn=self.merchant.msisdn,
                batch_trid=self.batch_trid
        )

    class Meta:
        verbose_name = 'BatchTransaction'
        verbose_name_plural = 'BatchTransactions'


class BatchTransactionLookup(models.Model):
    """
    This model defines an interface for retrieving individual transactions
    of a batch transaction
    """
    transaction = models.ForeignKey(Transaction)
    batch_transaction = models.ForeignKey(BatchTransaction, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{from_}: {to}".format(
                from_=self.batch_transaction.merchant,
                to=self.transaction.destination
        )

    class Meta:
        verbose_name = 'Batch Transaction Lookup'
        verbose_name_plural = 'Batch Transactions Lookup'



