from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class DebitMandate(models.Model):
    active = "active"
    inactive = "inactive"

    payer = models.ForeignKey(CustomerWallet, related_name="payer")
    payee = models.ForeignKey(CustomerWallet, related_name="payee")
    currency = models.CharField(max_length=10, default="KES")
    amount_limit = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    request_date = models.DateField()
    mandate_reference = models.UUIDField(unique=True)
    mandate_status = models.CharField(max_length=20)
    number_of_payments = models.IntegerField(default=1)
    min_amount_due = models.IntegerField(default=1)
    frequency_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{payer}: {payee}".format(
                biller=self.payer,
                billee=self.payee
        )

    class Meta:
        verbose_name = 'Debit Mandate'
        verbose_name_plural = 'Debit Mandates'

