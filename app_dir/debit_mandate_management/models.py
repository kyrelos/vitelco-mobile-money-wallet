from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class DebitMandate(models.Model):
    """
    The Debit Mandates API is used to enable a mobile money customer
    to provide prior approval for payments to be taken from their
    account by the indicated payee. If the amount property is
    not supplied, the mandate is considered open, i.e. the
    payer would be able to take any amount. Due to the need to obtain
    explicit payer approval, requests for mandates are typically
     asynchronous in nature. Mandates can be created,
     changed and inactivated. The URI format is as follows:
        -	Creation: POST /accounts/{Account Identifiers}/debitmandates.
        -	Update: In order to update a debit mandate,
            a HTTP PATCH is used.
            Format is: PATCH
            /accounts/{Account Identifiers}/debitmandates/{Mandate Reference}
        -   Read. GET
            /accounts/{Account Identifiers}/debitmandates/{Mandate Reference}.
    """
    active, inactive = "active", "inactive"
    daily, weekly, biweekly, monthly, yearly = 'daily', 'weekly', \
                                               'biweekly', 'monthly', \
                                               'yearly'
    FREQUENCY_TYPES = (
        (daily, daily),
        (weekly, weekly),
        (biweekly, biweekly),
        (monthly, monthly),
        (yearly, yearly)
    )

    MANDATE_STATUS = (
        (active, active),
        (inactive, inactive)
    )

    payer = models.ForeignKey(CustomerWallet, related_name="payer")
    payee = models.ForeignKey(CustomerWallet, related_name="payee")
    currency = models.CharField(max_length=10, default="KES")
    amount_limit = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    request_date = models.DateField()
    mandate_reference = models.UUIDField(unique=True)
    mandate_status = models.CharField(max_length=20,
                                      choices=MANDATE_STATUS,
                                      default=active)
    number_of_payments = models.IntegerField(default=1)
    min_amount_due = models.IntegerField(default=1)
    frequency_type = models.CharField(max_length=20,
                                      choices=FREQUENCY_TYPES,
                                      default=monthly)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{payer}: {payee}".format(
                payer=self.payer,
                payee=self.payee
        )

    class Meta:
        verbose_name = 'Debit Mandate'
        verbose_name_plural = 'Debit Mandates'

