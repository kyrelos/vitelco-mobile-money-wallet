from django.conf.urls import include, url
from django.contrib import admin
from app_dir.notification_management import urls as notification_urls
from app_dir.customer_wallet_management import urls as customer_wallet_urls


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/notification/', include(notification_urls)),
    url(r'^api/v1/wallet/', include(customer_wallet_urls)),
]
