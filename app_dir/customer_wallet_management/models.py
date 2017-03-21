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
        from app_dir.wallet_transactions.models import Transaction, \
            WalletTopupTransaction

        debit_query = Transaction.objects.filter(
                destination=self,
                state__in=['completed', 'reversed']
        )
        debit_amounts = 0.00
        if debit_query:
            debit_amounts = debit_query. \
                    aggregate(Sum('amount')). \
                    get('amount__sum', 0.00)

        topup_query = WalletTopupTransaction.objects.filter(
                wallet=self
        )
        total_topups = 0.00
        if topup_query:
            total_topups = topup_query. \
                aggregate(Sum('amount')). \
                get('amount__sum', 0.00)

        credit_query = Transaction.objects.filter(
                source=self,
                state__in=['completed', 'in_progress', 'reversed', 'pending']
        )
        credit_amounts = 0.00
        if credit_query:
            credit_amounts = credit_query. \
                aggregate(Sum('amount')). \
                get('amount__sum', 0.00)
        balance = (debit_amounts + total_topups) - credit_amounts
        return balance

    def get_actual_balance(self):
        from app_dir.wallet_transactions.models import Transaction, \
            WalletTopupTransaction

        topup_query = WalletTopupTransaction.objects.filter(
                wallet=self
        )
        total_topups = 0.00
        if topup_query:
            total_topups = topup_query. \
                aggregate(Sum('amount')). \
                get('amount__sum', 0.00)

        debit_query = Transaction.objects.filter(
                destination=self,
                state__in=['completed', 'in_progress', 'reversed']
        )

        debit_amounts = 0.00
        if debit_query:
            debit_amounts = debit_query. \
                aggregate(Sum('amount')). \
                get('amount__sum', 0.00)

        credit_query = Transaction.objects.filter(
                source=self,
                state__in=['completed', 'in_progress', 'reversed']
        )
        credit_amounts = 0.00
        if credit_query:
            credit_amounts = credit_query. \
                aggregate(Sum('amount')). \
                get('amount__sum', 0.00)

        balance = (debit_amounts + total_topups) - credit_amounts
        return balance

    def get_account_transactions(self):
        from app_dir.wallet_transactions.models import Transaction
        transactions = Transaction.objects.filter(Q(
            destination=self) | Q(source=self)).order_by(
            '-created_at')[:5]

        return transactions

    def get_account_bills(self):
        from app_dir.bill_management.models import Bill
        bills = Bill.objects.filter(billee=self)

        return bills

    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'

