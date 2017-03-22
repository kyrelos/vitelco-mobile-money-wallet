from __future__ import absolute_import

from celery import shared_task
from django.conf import settings

from app_dir.notification_management.models import Notification
from app_dir.notification_management.tasks import send_normal_notification, \
    send_push_notification
from .models import Transaction
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
    logger.info('process_transaction_start', trid=transaction_id)
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
            logger.info('process_transaction_notify_push',
                        trid=transaction_id,
                        notid=notification.notid
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
            send_push_notification.delay(notification.notid, transaction_id)
            logger.info('process_transaction_notify_normal',
                        trid=transaction_id,
                        notid=notification.notid
                        )


@shared_task
def complete_push_transactions(transaction_id):
    transaction = Transaction.objects.get(transaction_id=transaction_id)
