from __future__ import absolute_import

import json
import uuid
from datetime import datetime
from django.utils import timezone

import requests
from celery import shared_task
from requests import RequestException

from app_dir.notification_management.models import Notification
from app_dir.notification_management.tasks import send_normal_notification, \
    send_push_notification
from .models import Transaction, DebitMandate
from structlog import get_logger

logger = get_logger('celery')

API_HEADERS = {
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
    transaction_id = str(transaction_id)
    logger.info('process_transaction_start', trid=transaction_id)
    transaction = Transaction.objects.get(trid=transaction_id)
    current_state = transaction.state
    if current_state == "pending":
        transaction.start_transaction()
        transaction.save()
        if transaction.transaction_type in ["merchantPayment", "billPay"]:
            notification = Notification.objects.create(
                notification_type="push",
                customer=transaction.destination,
                message="Please enter Pin to complete transaction"

            )
            send_push_notification.delay(str(notification.notid),
                                         transaction_id)
            logger.info('process_transaction_notify_push',
                        trid=transaction_id,
                        notid=str(notification.notid)
                        )

        else:
            transaction.complete_transaction()
            transaction.save()
            notification = Notification.objects.create(
                notification_type="normal",
                customer=transaction.destination,
                message="you have transacted with viteco mobile wallet"

            )
            send_normal_notification.delay(notification.notid, transaction_id)
            logger.info('process_transaction_notify_normal',
                        trid=transaction_id,
                        notid=str(notification.notid)
                        )


@shared_task
def process_debit_mandate(mandate_reference, url):
    debit_mandate = DebitMandate.objects.get(
        mandate_reference=mandate_reference
    )

    frequency_map = {
        "minutely":1
    }

    timestamp = timezone.now()

    if debit_mandate.mandate_status == "active":
        if debit_mandate.end_date > timestamp:
            if debit_mandate.number_of_payments > 0:
                debitParty = debit_mandate.payer
                creditParty = debit_mandate.payee
                amount = debit_mandate.amount_limit
                transaction_payload = {
                    "requestingOrganisationTransactionReference": "MWCAPIWorkshop001",
                    "debitParty": [
                        {"value": debitParty.msisdn,
                         "key": "msisdn"}
                    ],
                    "currency": debit_mandate.currency,
                    "amount": amount,
                    "requestDate": timestamp.isoformat(), "creditParty": [
                        {"value": creditParty.msisdn,
                         "key": "msisdn"}
                    ],
                    "type": "transfer"
                }

                try:
                    server_correlation_id = str(uuid.uuid4())
                    headers = {
                        "X-CORRELATIONID": server_correlation_id,
                        "Authorization": "api-key",
                        "Content-type": "application/json"
                    }
                    logger.info("process_debit_mandate_payload",
                                url=url,
                                payload=transaction_payload)

                    response = requests.post(url,
                                             data=json.dumps(
                                                 transaction_payload),
                                             headers=headers
                                             )
                    if response.status_code in (202, 201):
                        debit_mandate.number_of_payments -= 1
                        debit_mandate.save()

                        if frequency_map.get(debit_mandate.frequency_type):
                            process_debit_mandate.apply_async(
                                args=[mandate_reference, url],
                                countdown=60
                            )
                        else:
                            """TODO: When we are not working on hackathon"""
                            pass

                    logger.info("process_debit_mandate_response",
                                response=str(response.text),
                                status_code=str(response.status_code))

                except RequestException as e:
                    logger.exception("process_debit_mandate_exception",
                                     exception=e.message
                                     )

