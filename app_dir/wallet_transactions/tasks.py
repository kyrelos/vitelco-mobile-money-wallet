from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from .models import Transaction
from app_dir.notification_management.models import Notification
import requests
import json
from app_dir.notification_management.tasks import send_normal_notification, \
    send_push_notification

API_HEADERS = {
        "Authorization": settings.API_KEY,
        "Content-Type": "application/json",
        "Accept": 'application/json'
    }



@shared_task
def process_transaction(transaction_id):
    """
    This task processes the received transaction accordingly
    :param notification_id:
    :return:
    """
    transaction = Transaction.objects.get(trid=transaction_id)
    current_state = transaction.state
    if current_state == "pending":
        transaction.start_transaction()
        transaction.save()
        if transaction.transaction_type in ["merchantpay", "billpay"]:
            notification = Notification.objects.create(
                    notification_type="push",
                    customer=transaction.destination,
                    message="Please enter Pin to complete transaction"

            )
            send_push_notification.delay(notification.notid, transaction_id)

        else:
            transaction.complete_transaction()
            transaction.save()
            notification = Notification.objects.create(
                    notification_type="normal",
                    customer=transaction.destination,
                    message="you have transacted with viteco mobile wallet"

            )
            send_normal_notification.delay(notification.notid, transaction_id)


@shared_task
def complete_push_transactions(transaction_id):
    transaction = Transaction.objects.get(transaction_id=transaction_id)


