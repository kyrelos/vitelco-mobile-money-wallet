from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CustomerWalletViewSet.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', views.CustomerWalletViewSet.as_view()),
    url(r'^msisdn/(?P<msisdn>[0-9]+)/status/$', views.getAccountStatus.as_view()),
    url(r'^msisdn/(?P<msisdn>[0-9]+)/balance/$', views.AccountBalanceByMsisdn.as_view()),
    url(r'^(?P<account_id>[\w\-]+)/balance/$', views.AccountBalanceByAccountId.as_view()),
    url(r'^msisdn/(?P<msisdn>[0-9]+)/accountname/$', views.GetAccountName.as_view())
]
