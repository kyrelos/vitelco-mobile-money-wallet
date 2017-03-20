from django.conf.urls import url
from .views import GetTransaction
from app_dir.wallet_transactions.views import CreateTransactions

urlpatterns = [
    url(r'^(?P<transaction_reference>[0-9a-zA-Z\-]+)/$',
        GetTransaction.as_view(),
        name='get_transaction_by_transaction_reference'),
    url(r'$', CreateTransactions.as_view(),
        name='create_transactions'),
    url(r'^(?P<batch_trid>[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[1345][a-fA-F0-9]{3}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12})$',
        GetBatchTransaction.as_view(),
        name='get_batch_transaction'),
    url(r'$', BatchTransactions.as_view(), name='batchtransactions'),
]

