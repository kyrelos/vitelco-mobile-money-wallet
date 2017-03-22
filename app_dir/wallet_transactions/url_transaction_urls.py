from django.conf.urls import url
from .views import GetTransaction
from app_dir.wallet_transactions.views import CreateTransactions

urlpatterns = [
    url(r'^(?P<transaction_reference>[0-9a-zA-Z\-]+)$',
        GetTransaction.as_view(),
        name='get_transaction_by_transaction_reference'),
    url(r'$', CreateTransactions.as_view(),
        name='create_transactions'),
]

