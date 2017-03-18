from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.CustomerWalletViewSet.as_view(),
        name="list_customer_wallet"),
    url(r'^(?P<pk>[0-9]+)/$', views.CustomerWalletViewSet.as_view(),
        name="customer_wallet_detail"),
    url(r'^msisdn/(?P<msisdn>[+][0-9]+)/status/$',
        views.GetAccountStatusByMsisdn.as_view(),
        name="msisdn"),
    url(r'^(?P<wallet_id>[0-9a-zA-z\-]+)/status/$',
        views.GetAccountStatusByAccountId.as_view(),
        name="get_account_status_by_account_id"),
    url(r'^msisdn/(?P<msisdn>[0-9]+)/accountname/$',
        views.GetAccountNameByMsisdn.as_view(),
        name="get_account_name_by_msisdn"),
    url(r'^msisdn/(?P<msisdn>[0-9]+)/balance/$',
        views.AccountBalanceByMsisdn.as_view(),
        name="get_account_balance_by_msisdn"),
    url(r'^(?P<account_id>[\w\-]+)/balance/$',
        views.AccountBalanceByAccountId.as_view(),
        name="get_account_balance_by_account_id"),

]
