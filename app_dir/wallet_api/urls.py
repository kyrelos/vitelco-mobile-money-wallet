from django.conf.urls import url

from app_dir.wallet_api.views import BatchTransactions

urlpatterns = [
    # shorter blob that allows for more flexible params [^/]+
    url(r'^(?P<batch_trid>[a-fA-F0-9]{8}-?[a-fA-F0-9]{4}-?[1345][a-fA-F0-9]{3}-?[a-fA-F0-9]{4}-?[a-fA-F0-9]{12})$',
        BatchTransactions.as_view(),
        name='get_batch_transaction'),
    url(r'$', BatchTransactions.as_view(), name='batchtransactions'),
]

