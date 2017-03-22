from django.conf.urls import url
from app_dir.bill_management.views import CreateBillPayment

urlpatterns = [
    url(r'^(?P<bill_reference>[\w\-]+)/payments', CreateBillPayment.as_view(),
        name='create_transactions')]
