import uuid
import json
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from rest_framework import status

from app_dir.customer_wallet_management.models import CustomerWallet
from .models import BatchTransaction, \
    BatchTransactionLookup, Transaction


class BatchTransactionsApiTest(TestCase):
    """
    Basic functionality testing for batch transaction requests
    """

    def setUp(self):
        # not the best way to setup dummy data
        # make this more elegant later
        self.wallet_info = {
            "msisdn": "254719917269",
            "token": str(uuid.uuid4()),
            "name": "ACME Inc",
            "balance": "10000"
        }
        self.wallet = CustomerWallet(**self.wallet_info)
        self.wallet.save()

        self.batch_transaction = BatchTransaction.objects.create(
            merchant=self.wallet, batch_status=BatchTransaction.BATCH_STATUS[0]
        )

        source_wallet = CustomerWallet.objects.create(
            msisdn="254719917270", token=str(uuid.uuid4()),
            name="Road Runner", balance=0
        )
        destination_wallet = CustomerWallet.objects.create(
            msisdn="254719917271", token=str(uuid.uuid4()),
            name="Will E Coyote", balance=0
        )
        trn1 = Transaction.objects.create(
            trid=uuid.uuid4(), source=source_wallet,
            destination=destination_wallet, amount=1000,
            server_correlation_id=uuid.uuid4(), transaction_type="deposit",
            state="failed"
        )
        trn2 = Transaction.objects.create(
            trid=uuid.uuid4(), source=source_wallet,
            destination=destination_wallet, amount=1000,
            server_correlation_id=uuid.uuid4(), transaction_type="deposit",
            state="in_progress"
        )
        trn3 = Transaction.objects.create(
            trid=uuid.uuid4(), source=source_wallet,
            destination=destination_wallet, amount=1000,
            server_correlation_id=uuid.uuid4(), transaction_type="deposit",
            state="reversed"
        )
        trn4 = Transaction.objects.create(
            trid=uuid.uuid4(), source=source_wallet,
            destination=destination_wallet, amount=1000,
            server_correlation_id=uuid.uuid4(), transaction_type="deposit",
            state="completed"
        )

        BatchTransactionLookup.objects.create(
            transaction=trn1, batch_transaction=self.batch_transaction
        )
        BatchTransactionLookup.objects.create(
            transaction=trn2, batch_transaction=self.batch_transaction
        )
        BatchTransactionLookup.objects.create(
            transaction=trn3, batch_transaction=self.batch_transaction
        )
        BatchTransactionLookup.objects.create(
            transaction=trn4, batch_transaction=self.batch_transaction
        )

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
            response_dict['reference'],
            str(self.batch_transaction.batch_trid)
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

    def test_batch_transaction_by_state(self):
        response = self.client.get(
            reverse(
                "get_batch_transaction_by_state", kwargs={
                    "batch_trid": self.batch_transaction.batch_trid,
                    "state": "rejections"
                }
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = json.loads(response.content)
        self.assertEqual(
            response_dict['reference'],
            str(self.batch_transaction.batch_trid)
        )

    def test_batch_transaction_completed_transactions(self):
        response = self.client.get(
            reverse(
                "get_batch_transaction_by_state", kwargs={
                    "batch_trid": self.batch_transaction.batch_trid,
                    "state": "completions"
                }
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_dict = json.loads(response.content)
        self.assertEqual(
            response_dict['reference'],
            str(self.batch_transaction.batch_trid)
        )

    def test_batch_transaction_invalid_state(self):
        response = self.client.get(
            reverse(
                "get_batch_transaction_by_state", kwargs={
                    "batch_trid": self.batch_transaction.batch_trid,
                    "state": "completion"
                }
            ),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
