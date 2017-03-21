from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class Bill(models.Model):
    """
    The Bills API is used to return all outstanding bills
    associated with an account. The main purpose of the object
    is to support Bill Presentment, i.e. presenting all applicable
    bills for a payer to view and select for payment. In order to
    pay a bill, the Transactions object is used.
    The URI format is as follows
    follows - '/accounts/{Account Identifiers}/bills'. Only GET (read)
    operations are permitted for the Bills object.

    """
    biller = models.ForeignKey(CustomerWallet, related_name="biller")
    billee = models.ForeignKey(CustomerWallet, related_name="billee")
    currency = models.CharField(max_length=10, default="KES")
    amount_due = models.IntegerField()
    due_date = models.DateField()
    bill_reference = models.UUIDField(unique=True)
    min_amount_due = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    bill_description = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return "{biller}: {billee}".format(
            biller=self.biller,
            billee=self.billee
        )

    class Meta:
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'

