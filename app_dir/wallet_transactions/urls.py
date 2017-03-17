from django.conf.urls import url
from .views import TransactionCreateList


urlpatterns = [
    url(r'^list_create', TransactionCreateList.as_view(),
        name='list_create_transaction '),



]

