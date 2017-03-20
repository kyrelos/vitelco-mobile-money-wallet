import uuid
import json
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from rest_framework import status

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.models import BatchTransaction


class BatchTransactionsApiTest(TestCase):
    """
    Basic functionality testing for batch transaction requests
    """

    def setUp(self):
        self.wallet_info = {
            "msisdn": "254719917267",
            "token": str(uuid.uuid4()),
            "name": "ACME Inc",
            "balance": "10000"
        }
        self.wallet = CustomerWallet(**self.wallet_info)
        self.wallet.save()
        self.batch_transaction = BatchTransaction(merchant=self.wallet)
        self.batch_transaction.save()

        self.headers = {
            "HTTP_DATE": "Tue, 28 Feb 2017 16:12:31 GMT",
        }
        self.client = Client(**self.headers)

    def test_batch_transaction_retrieval(self):
        response = self.client.get(
            reverse(
                "get_batch_transaction", kwargs={
                    "batch_trid":
                        self.batch_transaction.batch_trid
                }
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = json.loads(response.content)
        self.assertEqual(
            response_dict['transaction']['merchant']['name'],
            self.wallet_info['name']
        )
        self.assertEqual(
            response_dict['transaction']['merchant']['msisdn'],
            self.wallet_info['msisdn']
        )
        self.assertEqual(
            response_dict['transaction']['merchant']['wallet_id'],
            str(self.wallet.wallet_id)
        )

    def test_batch_transaction_retrieval_missing_uuid(self):
        response = self.client.get(
            reverse(
                "get_batch_transaction", kwargs={
                    "batch_trid": uuid.uuid4()
                }
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
