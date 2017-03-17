from django.contrib import admin
from .models import Transaction, BatchTransaction, BatchTransactionLookup

admin.site.register(Transaction)
admin.site.register(BatchTransaction)
admin.site.register(BatchTransactionLookup)
