from django.conf.urls import url
from .views import NotificationList, UpdateNotification


urlpatterns = [
    url(r'^list_create', NotificationList.as_view(), name='notifications'),
    url(r'^update', UpdateNotification.as_view(),
        name='update_notifications'),


]

