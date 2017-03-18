from django.db import models
from app_dir.customer_wallet_management.models import CustomerWallet


class Bill(models.Model):
    biller = models.ForeignKey(CustomerWallet, related_name="biller")
    billee = models.ForeignKey(CustomerWallet, related_name="billee")
    currency = models.CharField(max_length=10, default="KES")
    amount_due = models.IntegerField()
    due_date = models.DateField()
    bill_reference = models.UUIDField(unique=True)
    min_amount_due = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{biller}: {billee}".format(
            biller=self.biller,
            billee=self.billee
        )

    class Meta:
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'

