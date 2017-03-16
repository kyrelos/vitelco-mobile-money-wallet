from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^wallets/$', views.wallets_list),
]
