from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from .models import Notification
import requests
import json

API_HEADERS = {
        "Authorization": settings.API_KEY,
        "Content-Type": "application/json",
        "Accept": 'application/json'
    }



@shared_task
def send_notification(notification_id):
    """
    This task sends transaction notification to the customer
    :param notification_id:
    :return:
    """
    notification = Notification.objects.get(notid=notification_id)

