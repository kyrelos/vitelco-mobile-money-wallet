from django.conf.urls import url
from .views import GetTransaction


urlpatterns = [
    url(r'^(?P<transaction_reference>[0-9a-zA-Z\-]+)/$', GetTransaction.as_view(),
        name='transaction_retrieve '),



]

