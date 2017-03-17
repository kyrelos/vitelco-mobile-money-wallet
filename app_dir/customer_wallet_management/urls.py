from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.CustomerWalletViewSet.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', views.CustomerWalletViewSet.as_view()),
    url(r'^msisdn/(?P<msisdn>[+][0-9]+)/status/$',
        views.GetAccountStatusByMSISDN.as_view()),
    url(r'^(?P<wallet_id>[0-9a-zA-z\-]+)/status/$',
        views.GetAccountStatusByUUID.as_view()),
    url(r'^msisdn/(?P<msisdn>[0-9]+)/accountname/$',
        views.GetAccountName.as_view())
]

