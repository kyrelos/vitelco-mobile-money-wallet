from django.conf.urls import url
from .views import CustomerWalletView, CustomerWalletList

urlpatterns = [
    url(r'^retrieve_update/(?P<wallet_id>[\w\-]+)/$', CustomerWalletView.as_view(), name='retrieve_update_wallet'),
    url(r'^list_create/', CustomerWalletList.as_view(), name='list_create_wallet'),

]
