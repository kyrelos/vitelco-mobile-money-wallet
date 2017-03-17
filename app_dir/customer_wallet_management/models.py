import uuid

from django.db import models
from django.db.models import Sum


class CustomerWallet(models.Model):
    """
    This model defines The Customer and thier attributes

    msisdn: phone number of the customer
    token: unique notification token of the customer
    name: name of the customer
    type: type of the customer
    """
    CUSTOMER_TYPES = (
        ("normal", "normal"),
        ("merchant", "merchant")
    )

    CUSTOMER_STATUS_TYPES = (
        ("active", "active"),
        ("dormant", "dormant"),
        ("inactive", "inactive")
    )

    wallet_id = models.UUIDField(unique=True, default=uuid.uuid4)
    msisdn = models.CharField(max_length=20, unique=True)
    token = models.CharField(max_length=256, unique=True, null=True)
    name = models.CharField(max_length=120)
    status = models.CharField(max_length=20,
                              choices=CUSTOMER_STATUS_TYPES,
                              default="active"
                              )
    type = models.CharField(max_length=20,
                            choices=CUSTOMER_TYPES,
                            default="normal"
                            )
    balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{name}: {msisdn}".format(
            name=self.name,
            msisdn=self.msisdn
        )

    def get_available_balance(self):
        from app_dir.wallet_transactions.models import Transaction
        debit_amounts = Transaction.objects.filter(destination=self.wallet_id, state='completed').aggregate(
            Sum('amount'))
        credit_amounts = Transaction.objects.filter(source=self.wallet_id, state='completed').aggregate(Sum('amount'))
        balance = debit_amounts - credit_amounts
        return balance

    def get_actual_balance(self):
        from app_dir.wallet_transactions.models import Transaction
        debit_amounts = Transaction.objects \
            .filter(destination=self.wallet_id, state__in=['completed', 'in_progress']).aggregate(Sum('amount'))
        credit_amounts = Transaction.objects \
            .filter(source=self.wallet_id, state__in=['completed', 'in_progress']).aggregate(Sum('amount'))
        balance = debit_amounts - credit_amounts
        return balance

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
