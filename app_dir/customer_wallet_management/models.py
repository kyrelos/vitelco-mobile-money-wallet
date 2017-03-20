import uuid

from django.db import models
from django.db.models import Sum
from django.db.models import Q


class CustomerWallet(models.Model):
    """
    This model defines The Customer and thier attributes

    msisdn: phone number of the customer
    token: unique notification token of the customer
    name: name of the customer
    type: type of the customer
    """
    active, dormant, inactive = "active", "dormant", "inactive"
    normal, merchant = "normal", "merchant"

    CUSTOMER_TYPES = (
        (normal, normal),
        (merchant, merchant)
    )

    CUSTOMER_STATUS_TYPES = (
        (active, active),
        (dormant, dormant),
        (inactive, inactive)
    )

    wallet_id = models.UUIDField(unique=True, default=uuid.uuid4)
    msisdn = models.CharField(max_length=20, unique=True)
    token = models.CharField(max_length=256, null=True, blank=True)
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
        debit_query = Transaction.objects.filter(
            destination=self.wallet_id, state='completed')
        debit_amounts = debit_query.aggregate(Sum('amount')).get(
            'amount__sum', 0.00) if debit_query else 0.0

        credit_query = Transaction.objects.filter(source=self.wallet_id,
                                                  state='completed')
        credit_amounts = credit_query.aggregate(Sum('amount')).get(
            'amount__sum', 0.00) if credit_query else 0.0
        balance = debit_amounts - credit_amounts
        return balance

    def get_actual_balance(self):
        from app_dir.wallet_transactions.models import Transaction
        debit_query = Transaction.objects.filter(
            destination=self.wallet_id, state__in=['completed', 'in_progress'])
        debit_amounts = debit_query.aggregate(Sum('amount')).get(
            'amount__sum', 0.00) if debit_query else 0.0

        credit_query = Transaction.objects.filter(source=self.wallet_id,
                                                  state__in=['completed',
                                                             'in_progress'])
        credit_amounts = credit_query.aggregate(Sum('amount')).get(
            'amount__sum', 0.00) if credit_query else 0.0
        balance = debit_amounts - credit_amounts
        return balance

    def get_account_transactions(self):
        from app_dir.wallet_transactions.models import Transaction
        transactions = Transaction.objects.filter(Q(
            destination=self) | Q(source=self))[:5]

        return transactions

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

