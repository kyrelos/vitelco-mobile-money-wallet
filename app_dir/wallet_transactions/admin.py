from django.contrib import admin
from .models import Transaction, BatchTransaction, BatchTransactionLookup, \
    WalletTopupTransaction, DebitMandate

class TransactionAdmin(admin.ModelAdmin):
    list_display = ["trid", "created_at", "modified_at", "amount",
                    "transaction_type", "source",
                    "destination"]
    search_fields = ["trid"]

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(BatchTransaction)
admin.site.register(BatchTransactionLookup)
admin.site.register(WalletTopupTransaction)
admin.site.register(DebitMandate)
