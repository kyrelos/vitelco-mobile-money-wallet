from django.conf.urls import url
from app_dir.bill_management.views import CreateBill

urlpatterns = [
    url(r'$', CreateBill.as_view(),
        name='create_bill')

]