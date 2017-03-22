from django.contrib import admin
from .models import Transaction, BatchTransaction, BatchTransactionLookup, \
    WalletTopupTransaction, DebitMandate

admin.site.register(Transaction)
admin.site.register(BatchTransaction)
admin.site.register(BatchTransactionLookup)
admin.site.register(WalletTopupTransaction)
admin.site.register(DebitMandate)
