from django.db import models


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
    msisdn = models.CharField(max_length=20, unique=True)
    token = models.CharField(max_length=256)
    name = models.CharField(max_length=120)
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

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
