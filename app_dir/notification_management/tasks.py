from __future__ import absolute_import

import requests
from celery import shared_task
from django.conf import settings
from requests import RequestException
from structlog import get_logger

from app_dir.wallet_transactions.models import Transaction
from .models import Notification

logger = get_logger('celery')

FCM_API_HEADERS = {
        "Authorization": settings.FCM_API_KEY,
        "Content-Type": "application/json",
        "Accept": 'application/json'
    }


@shared_task
def send_normal_notification(notification_id, transaction_id):
    """
    This task sends transaction notification to the customer
    :param notification_id:
    :param transaction_id:
    :return:
    """

    title = "Vitelco Transaction Message"
    notification = Notification.objects.get(notid=notification_id)
    message = notification.message
    notification_type = notification.notification_type

    notification_payload = {
        "to": notification.customer.token,
        "notification": {
            "body": message,
            "title": title
        },
        "data": {
            "message": message,
            "title": title,
            "message_type": notification_type,
            "notification_id": notification.notid,
            "transaction_id": transaction_id
        },
    }
    try:
        response = requests.post(settings.FCM_URL,
                                 data=notification_payload,
                                 headers=FCM_API_HEADERS
                                 )
        transaction = Transaction.objects.get(
                transaction_id=transaction_id
        )
        if response.status_code in (200, 202):
            notification.state = "success"
            notification.save()
            transaction.complete_transaction()
            transaction.save()

            logger.info('notification_success',
                        data=notification_payload,
                        status_code=response.status_code,
                        response=response.json()
                        )

        else:
            notification.state = "failed"
            notification.save()
            transaction.fail_transaction()
            transaction.save()
            logger.info('notification_failure',
                        data=notification_payload,
                        status_code=response.status_code,
                        response=response.json(),

                        )
    except RequestException as e:
        notification.state = "failed"
        notification.save()
        logger.info('notification_exception',
                    data=notification_payload,
                    exception=e.message

                    )


@shared_task
def send_push_notification(notification_id, transaction_id):
    """
    This task sends push notification to the customer
    :param notification_id:
    :param transaction_id:
    :return:
    """

    title = "Vitelco Transaction Message"
    notification = Notification.objects.get(notid=notification_id)
    message = notification.message
    notification_type = notification.notification_type

    notification_payload = {
        "to": notification.customer.token,
        "notification": {
            "body": message,
            "title": title
        },
        "data": {
            "message": message,
            "title": title,
            "message_type": notification_type,
            "notification_id": notification.notid,
            "transaction_id": transaction_id
        },
    }
    try:
        response = requests.post(settings.FCM_URL,
                                 data=notification_payload,
                                 headers=FCM_API_HEADERS
                                 )
        if response.status_code in (200, 202):
            notification.state = "success"
            notification.save()

            logger.info('send_push_notification_success',
                        data=notification_payload,
                        status_code=response.status_code,
                        response=response.json()
                        )

        else:
            notification.state = "failed"
            notification.save()
            transaction = Transaction.objects.get(
                    transaction_id=transaction_id
            )
            transaction.fail_transaction()
            transaction.save()
            logger.info('send_push_notification_failure',
                        data=notification_payload,
                        status_code=response.status_code,
                        response=response.json(),

                        )
    except RequestException as e:
        notification.state = "failed"
        notification.save()
        transaction = Transaction.objects.get(
                transaction_id=transaction_id
        )
        transaction.fail_transaction()
        transaction.save()
        logger.info('notification_exception',
                    data=notification_payload,
                    exception=e.message

                    )
