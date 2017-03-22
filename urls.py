from django.conf.urls import include, url
from django.contrib import admin
from app_dir.notification_management import urls as notification_urls
from app_dir.customer_wallet_management import urls as customer_wallet_urls
from app_dir.wallet_transactions import url_transaction_urls
from app_dir.wallet_api.views import APIRootView
from app_dir.wallet_transactions import url_batch_transaction_urls
from app_dir.wallet_transactions.views import GetTransactionState, \
    GetStatementByTransactionID
from app_dir.bill_management import urls as bill_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/$', APIRootView.as_view(),
        name="api"),
    url(r'^api/v1/notification/',
        include(notification_urls,
                namespace='notify',
                app_name="notification_management")),
    url(r'^api/v1/accounts/',
        include(customer_wallet_urls,
                namespace='account',
                app_name="customer_wallet_management"
                )),
    url(r'^api/v1/transactions/', include(url_transaction_urls)),
    url(r'^api/v1/batchtransactions/', include(url_batch_transaction_urls)),
    url(r'^api/v1/requeststates/(?P<server_correlation_id>[\w\-]+)$',
        GetTransactionState.as_view(),
        name="get_transaction_state"),
    url(r'^api/v1/statemententries/(?P<trid>[0-9a-zA-z\-]+)$',
        GetStatementByTransactionID.as_view(),
        name="get_statement_by_trid"),
    url(r'^api/v1/bills/(?P<bill_reference>[\w\-]+)/payments$',
        include(bill_urls))
]
