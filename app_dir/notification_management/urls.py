from django.conf.urls import  url
from .views import NotificationList


urlpatterns = [
    url(r'^list_create', NotificationList.as_view(), name='notification '),


]

