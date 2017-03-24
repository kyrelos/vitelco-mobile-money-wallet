import uuid
from django.db import models
from datetime import datetime

from django_fsm import FSMField, transition

from app_dir.customer_wallet_management.models import CustomerWallet


class Transaction(models.Model):
    """
    This model defines a transaction, i.e. Movement of cash from one wallet
    to another
    """

    pending, in_progress, completed, failed, reversed_ = "pending", \
                                                         "in_progress", \
                                                         "completed", \
                                                         "failed", \
                                                         "reversed"

    reversal, bill_pay, deposit, transfer, = "reversal", "billPay", \
                                            "deposit", "transfer"
    withdrawal, disbursement, merchant_payment = "withdrawal", "disbursement", \
                                            "merchantPayment"

    TRANSACTION_STATES = (
        (pending, pending),
        (in_progress, in_progress),
        (completed, completed),
        (failed, failed),
        (reversed_, reversed_)
    )

    TRANSACTION_TYPES = (
        (reversal, reversal),
        (bill_pay, bill_pay),
        (deposit, deposit),
        (transfer, transfer),
        (withdrawal, withdrawal),
        (disbursement, disbursement),
        (merchant_payment, merchant_payment),
    )
    trid = models.UUIDField(unique=True, default=uuid.uuid4)
    currency = models.CharField(max_length=10, default="KES")
    description_text = models.CharField(max_length=100, null=True, blank=True)
    request_date = models.DateTimeField(default=datetime(2017, 3, 22, 11, 2, 19, 767092))
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
    callback_url = models.URLField(null=True, blank=True)

    state = FSMField(max_length=20,
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

    @transition(field=state, source='pending', target='in_progress')
    def start_transaction(self):
        pass

    @transition(field=state,
                source='in_progress', target='failed')
    def fail_transaction(self):
        pass

    @transition(field=state,
                source='in_progress', target='completed')
    def complete_transaction(self):
        pass

    @transition(field=state, source='pending', target='reversed')
    def reverse_transaction(self):
        pass


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
    merchant = models.ForeignKey(CustomerWallet)
    processing = models.BooleanField(default=False)
    batch_title = models.TextField(null=False, default="BATCHTRX")
    batch_status = models.CharField(choices=BATCH_STATUS, max_length=20,
                                    default="created")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{batch_trid}".format(
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


class WalletTopupTransaction(models.Model):
    """
    This model solves the question as to how wallets are topped up and the
    source of the money being circulated in the mobile money wallets. It
    means that all wallet top-ups will be done at the bank.
    """
    bank_name = models.CharField(max_length=64)
    amount = models.IntegerField()
    currency = models.CharField(default="KES", max_length=10)
    bank_reference = models.CharField(max_length=64)
    deposit_timestamp = models.DateTimeField()
    wallet = models.ForeignKey(CustomerWallet)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{from_}: {to}".format(
            from_=self.bank_name,
            to=self.wallet
        )

    class Meta:
        verbose_name = 'Wallet Top-up Transaction'
        verbose_name_plural = 'Wallet Top-up Transactions'


class DebitMandate(models.Model):
    "This model stores all the debit mandates for particular accounts"

    weekly, fortnight, monthspecificdate, twomonths, threemonths, \
    fourmonths, sixmonths, yearly, lastdaymonth, lastdaymonthworking, \
    lastmonday, lasttuesday, lastwednesday, lastthursday, lastfriday, \
    lastsaturday, lastsunday, specificdaymonthly, minutely = "weekly", \
                                                             "fortnight", \
                                                             "monthspecificdate", \
                                                             "twomonths", \
                                                             "threemonths", \
                                                             "fourmonths", \
                                                             "sixmonths", "yearly", \
                                                             "lastdaymonth", \
                                                             "lastdaymonthworking", \
                                                             "lastmonday", \
                                                             "lasttuesday", \
                                                             "lastwednesday", \
                                                             "lastthursday", \
                                                             "lastfriday", \
                                                             "lastsaturday", \
                                                             "lastsunday", \
                                                             "specificdaymonthly", \
                                                             "minutely"

    FREQUECY_TYPE = (
        (weekly, weekly),
        (fortnight, fortnight),
        (monthspecificdate, monthspecificdate),
        (twomonths, twomonths, ),
        (threemonths, threemonths),
        (fourmonths, fourmonths),
        (sixmonths, sixmonths),
        (yearly, yearly),
        (lastdaymonth, lastdaymonth),
        (lastdaymonthworking, lastdaymonthworking),
        (lastmonday, lastmonday),
        (lasttuesday, lasttuesday),
        (lastwednesday, lastwednesday),
        (lastthursday, lastthursday),
        (lastfriday, lastfriday),
        (lastsaturday, lastsaturday),
        (lastsunday, lastsunday),
        (specificdaymonthly, specificdaymonthly),
        (minutely, minutely)
    )

    MANDATE_STATUS = (
        ("active", "active"),
        ("inactive", "inactive")
    )
    payer = models.ForeignKey(CustomerWallet, related_name="payer", null=True)
    payee = models.ForeignKey(CustomerWallet, related_name="payee", null=True)
    currency = models.CharField(default="KES", max_length=10)
    amount_limit = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    mandate_reference = models.UUIDField(unique=True, default=uuid.uuid4)
    number_of_payments = models.IntegerField()
    frequency_type = models.CharField(max_length=20,
                                     choices=FREQUECY_TYPE)
    mandate_status = models.CharField(max_length=20,
                                      choices=MANDATE_STATUS)
    request_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return "{payer}: {payee}".format(
                payer=self.payer,
                payee=self.payee
        )
