from django.conf.urls import url
from .views import TransactionCreateList
from app_dir.wallet_api.views import Transactions

urlpatterns = [
    url(r'^(?P<transaction_reference>[0-9a-zA-Z\-]+)/$',
        GetTransaction.as_view(),
        name='get_transaction_by_transaction_reference'),
    url(r'^list_create', Transactions.as_view(),
        name='list_create_transaction '),
]

