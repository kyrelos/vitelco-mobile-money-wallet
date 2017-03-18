from django.conf.urls import include, url
from django.contrib import admin
from app_dir.notification_management import urls as notification_urls
from app_dir.customer_wallet_management import urls as customer_wallet_urls
from app_dir.wallet_transactions import urls as transaction_urls
from app_dir.wallet_api import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/$', views.APIRootView.as_view(),
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
    url(r'^api/v1/transactions/', include(transaction_urls)),
    url(r'^api/v1/batchtransactions', views.BatchTransactions.as_view(),
        name="batchtransactions"),
]
