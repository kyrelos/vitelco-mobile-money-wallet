from django.contrib import admin
from .models import Transaction, BulkTransaction, BulkTransactionLookup

admin.site.register(Transaction)
admin.site.register(BulkTransaction)
admin.site.register(BulkTransactionLookup)
