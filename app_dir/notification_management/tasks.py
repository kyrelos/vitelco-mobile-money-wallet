from __future__ import absolute_import

import json

import requests
from celery import shared_task
from django.conf import settings
from requests import RequestException
from structlog import get_logger

from app_dir.wallet_transactions.models import Transaction
from .models import Notification

logger = get_logger('celery')

FCM_API_HEADERS = {
    "Authorization": "key=" + settings.FCM_API_KEY,
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

    notification = Notification.objects.get(notid=notification_id)
    transaction_id = str(transaction_id)
    transaction = Transaction.objects.get(trid=transaction_id)
    source = transaction.source
    destination = transaction.destination

    source_message = "You have sent {currency} {amount} to " \
                     "{name} {destination} successfully. " \
                     "Transaction Reference: {trid}".format(
            currency=transaction.currency,
            amount=transaction.amount,
            name=destination.name,
            destination=destination.msisdn,
            trid=transaction.trid

    )

    destination_message = "You have received {currency} {amount} from " \
                          "{name} {source} successfully. " \
                          "Transaction Reference: {trid}".format(
            currency=transaction.currency,
            amount=transaction.amount,
            name=source.name,
            source=source.msisdn,
            trid=transaction.trid

    )

    source_notification_payload = {
        "data": {
            "v_message": source_message,
            "v_message_type": "normal"
        },
        "to": source.get_token
    }

    destination_notification_payload = {
        "data": {
            "v_message": destination_message,
            "v_message_type": "normal"
        },
        "to": destination.get_token
    }
    try:
        source_response = requests.post(settings.FCM_URL,
                                        data=json.dumps(
                                            source_notification_payload),
                                        headers=FCM_API_HEADERS
                                        )

    except RequestException as e:

        destination_response = requests.post(settings.FCM_URL,
                                             data=json.dumps(
                                                     destination_notification_payload),
                                             headers=FCM_API_HEADERS
                                             )
        if source_response.status_code in (200, 202) and \
                        destination_response.status_code \
                in (200, 202):
            notification.state = "success"
            notification.save()
            # transaction.complete_transaction()
            # transaction.save()

            logger.info('notification_success',
                        source=source_notification_payload,
                        destination=destination_notification_payload,
                        source_status_code=source_response.status_code,
                        destination_status_code=destination_response
                        .status_code,
                        source_response=str(source_response.text),
                        destination_response=str(destination_response.text)
                        )

        else:
            notification.state = "failed"
            notification.save()
            # transaction.fail_transaction()
            # transaction.save()
            logger.info('notification_failure',
                        source=source_notification_payload,
                        destination=destination_notification_payload,
                        source_status_code=source_response.status_code,
                        destination_status_code=destination_response
                        .status_code,
                        source_response=str(source_response.text),
                        destination_response=str(destination_response.text)

                        )
    except RequestException as e:
        notification.state = "failed"
        notification.save()
        logger.info('notification_exception',
                    source=source_notification_payload,
                    destination=destination_notification_payload,
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
    transaction_id = str(transaction_id)
    notification_id = str(notification_id)
    transaction = Transaction.objects.get(
            trid=transaction_id
    )

    notification = Notification.objects.get(
            notid=notification_id
    )
    message = notification.message
    notification_type = notification.notification_type

    notification_payload = {
        "to": transaction.source.get_token,
        "data": {
            "v_message": message,
            "v_message_type": notification_type,
            "v_notification_id": notification_id,
            "v_transaction_id": transaction_id
        },
    }
    try:
        response = requests.post(settings.FCM_URL,
                                 data=json.dumps(notification_payload),
                                 headers=FCM_API_HEADERS
                                 )
        if response.status_code in (200, 202):
            notification.state = "success"
            notification.save()

            logger.info('send_push_notification_success',
                        data=notification_payload,
                        status_code=response.status_code,
                        response=str(response.text)
                        )

        else:
            notification.state = "failed"
            notification.save()
            transaction.fail_transaction()
            transaction.save()
            logger.info('send_push_notification_failure',
                        data=notification_payload,
                        status_code=response.status_code,
                        response=response.text,

                        )
    except RequestException as e:
        notification.state = "failed"
        notification.save()
        transaction = Transaction.objects.get(
                trid=transaction_id
        )
        transaction.fail_transaction()
        transaction.save()
        logger.info('notification_exception',
                    data=notification_payload,
                    exception=e.message

                    )
