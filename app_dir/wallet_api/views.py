import uuid
from datetime import datetime
from time import gmtime, strftime
import requests
from django.conf import settings
from django.db import IntegrityError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.forms.models import model_to_dict
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from structlog import get_logger

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.models import BatchTransaction, \
    Transaction, BatchTransactionLookup
from app_dir.wallet_transactions.serializers import \
    BatchTransactionSerializer, BatchTransactionLookUpSerializer

logger = get_logger('transactions')


class APIRootView(APIView):
    def get(self, request):
        api_registry = {
            "Transactions": {
                "Get transaction by transaction_reference": reverse(
                    "get_transaction_by_transaction_reference",
                    request=request,
                    current_app="wallet_transactions",
                    kwargs={
                        "transaction_reference":
                            "753bcd19-7230-40ba-a975-09ac94ace0d2"
                    }

                ),
                "Create transactions": reverse(
                    "create_transactions",
                    request=request
                ),
                "Get transaction state": reverse(
                    "get_transaction_state",
                    request=request,
                    kwargs={
                        "server_correlation_id":
                            "753bcd19-7230-40ba-a975-09ac94ace0d2"
                    }
                )

            },
            "BatchTransactions": {
                "Create batch transactions": reverse(
                    "batchtransactions", request=request
                ),
                "Get batch transaction": reverse(
                    "get_batch_transaction", request=request
                )
            },
            "Account": {
                "Get Account status by msisdn": reverse(
                    "account:msisdn",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"msisdn": "+254711111111"}
                ),
                "Get Account status by accountId": reverse(
                    "account:get_account_status_by_account_id",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={
                        "wallet_id": "753bcd19-7230-40ba-a975-09ac94ace0d2"
                    }
                ),
                "Get Account name by msisdn": reverse(
                    "account:get_account_name_by_msisdn",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"msisdn": "254711111111"}
                ),
                "Get Account name by accountId": reverse(
                    "account:get_account_name_by_account_id",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"account_id":
                                "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),
                "Get Account balance by msisdn": reverse(
                    "account:get_account_balance_by_msisdn",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"msisdn": "254711111111"}
                ),
                "Get Account balance by accountId": reverse(
                    "account:get_account_balance_by_account_id",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"account_id":
                                "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),

            },
            "Notification": {
                "ListCreate Notifications": reverse(
                    "notify:notifications",
                    request=request,
                    current_app="notification_management"
                )
            }
        }
        return Response(api_registry)


def send_error_response(message="404",
                        key="msisdn",
                        value=None,
                        status=None,
                        ):
    """
    Creates and outputs given error message
    Parameters
    ----------
    message : error message
    key : key errorParameter
    value: value errorParameter
    status: status code
    Returns
    -------
    a application/json rest_framework.response
    """
    date_time = datetime.now().isoformat()
    error_payload = {
        "errorCategory": "businessRule",
        "errorCode": "genericError",
        "errorDescription": message,
        "errorDateTime": date_time,
        "errorParameters": [
            {
                "key": key,
                "value": value
            }
        ]
    }

    response = Response(data=error_payload,
                        status=status
                        )
    return response

class GetBatchTransaction(APIView):
    """
    This API allows retrieving a bulk transaction given an ID
    """
    def get(self, request, batch_trid=None):
        if not batch_trid:
            logger.info(
                "get_transaction_invalid_uuid",
                status=status.HTTP_400_BAD_REQUEST,
                batch_trid=batch_trid,
                key="batch_trid"
            )

            return send_error_response(
                message="Invalid UUID",
                key="batch_transaction_reference",
                status=status.HTTP_400_BAD_REQUEST
            )

        date = request.META.get("HTTP_DATE")
        if not date and not settings.DEBUG:
            logger.info(
                "get_bulk_transaction_400",
                message="DATE Header not supplied",
                status=status.HTTP_400_BAD_REQUEST,
                key="DATE"
            )

            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            batch_transactions = BatchTransactionLookup.objects.filter(
                batch_transaction__batch_trid=batch_trid
            )

            if not batch_transactions:
                logger.info(
                    "get_batch_transaction_404",
                    status=status.HTTP_404_NOT_FOUND,
                    batch_trid=batch_trid,
                    key="batch_trid"
                )

                return send_error_response(
                    message="Requested resource not available",
                    key="batch_transaction_reference",
                    value=batch_trid,
                    status=status.HTTP_404_NOT_FOUND
                )

            payload = {
                "reference": batch_trid,
                "transactions": []
            }

            for transaction in batch_transactions:
                payload['transactions'].append(
                    model_to_dict(transaction.transaction))

            response = Response(
                data=payload, status=status.HTTP_200_OK
            )
            logger.info(
                "get_batch_transaction_200",
                status=status.HTTP_200_OK,
                batch_trid=batch_trid
            )
            return response
        except ValueError:
            logger.info(
                "get_transaction_malformed_uuid",
                status=status.HTTP_404_NOT_FOUND,
                batch_trid=batch_trid,
                key="batch_trid"
            )

            return send_error_response(
                message="Malformed UUID",
                key="batch_transaction_reference",
                value=batch_trid,
                status=status.HTTP_404_NOT_FOUND
            )

class BatchTransactions(APIView):
    """
    This API posts batch transactions
      HTTP Method: POST
      URI: /api/v1/batchtransactions/

    ===== SAMPLE PAY LOAD ======
    {
  "batchTitle": "BatchMWCDemo",
  "batchDescription": "DemoMWCBatch",
  "processingFlag": true,
   "batchStatus": "created",
   "merchant":"<merchant_id>"
  "transactions":[
            {
          "amount": "456522",
          "currency": "UGX",
          "type": "transfer",
          "requestDate": "2017-02-28 16:00:00",
          "requestingOrganisationTransactionReference": "MWCAPIWorkshop001",
          "debitParty": [
            {
              "key": "msisdn",
              "value": "+4491509874561"
            }
          ],
          "creditParty": [
            {
              "key": "msisdn",
              "value": "+25691508523697"
            }
          ]
      },
      {
          "amount": "456522",
          "currency": "UGX",
          "type": "transfer",
          "requestDate": "2017-02-28 16:00:00",
          "requestingOrganisationTransactionReference": "MWCAPIWorkshop001",
          "debitParty": [
            {
              "key": "msisdn",
              "value": "+4491509874561"
            }
          ],
          "creditParty": [
            {
              "key": "msisdn",
              "value": "+25691508523697"
            }
          ]
      }
  ]
}
    """

    def get_object(self, pk):
        try:
            return BatchTransaction.objects.get(pk=pk)
        except BatchTransaction.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        batch_transactions = BatchTransaction.objects.all()
        serializer = BatchTransactionSerializer(batch_transactions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        batch_transaction = {
            "merchant": request.data["merchant"],
            "batch_title": request.data["batchTitle"],
            "batch_description": request.data["batchDescription"],
            "status": request.data["batchStatus"],
            "processing": request.data["processingFlag"]
        }

        serializer = BatchTransactionSerializer(data=batch_transaction)

        if serializer.is_valid():
            batch_trx = serializer.save()
            for data in request.data["transactions"]:
                server_correlation_id = uuid.uuid4()
                source_msisdn = data["debitParty"][0]["value"]
                source = CustomerWallet.objects.get(msisdn=source_msisdn)
                destination_msisdn = data["creditParty"][0]["value"]

                destination = CustomerWallet.objects.get(
                    msisdn=destination_msisdn)
                amount = data["amount"]
                transaction_type = data["type"]
                create_transaction_data = dict(
                    source=source,
                    server_correlation_id=server_correlation_id,
                    destination=destination,
                    amount=amount,
                    transaction_type=transaction_type
                )

                trx = Transaction.objects.create(
                    **create_transaction_data)

                batch_lookup = BatchTransactionLookup.objects.create(
                    batch_transaction=batch_trx,
                    transaction=trx)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return_errors = dict(
                batch_transaction_errors=serializer.error_messages, )
            return Response(return_errors,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateTransactions(APIView):
    """
      This API posts a transaction
      HTTP Method: POST
      URI: /api/v1/transactions/

      Required HTTP Headers:
      DATE: todays date
      AUTHORIZATION: api-key
      CONTENT-TYPE: application/json

      Example Payload:

      {
          "amount": "456522",
          "currency": "UGX",
          "type": "transfer",
          "requestDate": "2017-02-28 16:00:00",
          "requestingOrganisationTransactionReference": "MWCAPIWorkshop001",
          "debitParty": [
            {
              "key": "msisdn",
              "value": "+4491509874561"
            }
          ],
          "creditParty": [
            {
              "key": "msisdn",
              "value": "+25691508523697"
            }
          ]
      }

        Success Response:
        HTTP status Code: 201 Created
        # To be updated

    """

    def post(self, request):
        logger.info(request.META)

        error_message = None
        error_key = None
        try:
            server_correlation_id = request.META['HTTP_X_CORRELATIONID']
            # date = request.META["HTTP_DATE"]
        except KeyError as e:
            logger.info("create_transaction_400",
                        message="Required Headers not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        key=e.message
                        )
            return send_error_response(
                message="Required Headers not supplied",
                key=e.message,
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            data = request.data
            trid = str(uuid.uuid4())
            source_msisdn = data["debitParty"][0]["value"]
            source = CustomerWallet.objects.get(msisdn=source_msisdn)
            destination_msisdn = data["creditParty"][0]["value"]
            destination = CustomerWallet.objects.get(msisdn=destination_msisdn)
            amount = data["amount"]
            transaction_type = data["type"]
            create_transaction_data = dict(
                trid=trid,
                source=source,
                server_correlation_id=server_correlation_id,
                destination=destination,
                amount=amount,
                transaction_type=transaction_type
            )
            source_balance = source.get_available_balance()
            if transaction_type == 'transfer':
                if source_balance < amount:
                    insufficient_funds_response = send_error_response(
                        message="You have insufficient funds",
                        key="Balance",
                        value=source_balance,
                        status=status.HTTP_402_PAYMENT_REQUIRED
                    )
                    return insufficient_funds_response

        except KeyError as e:
            error_message = "Missing required field"
            key = e.message
            value = None
            status_code = status.HTTP_400_BAD_REQUEST

            error_response = send_error_response(
                message=error_message,
                key=key,
                value=value,
                status=status_code
            )
            logger.info("create_transaction_400",
                        status=status.HTTP_400_BAD_REQUEST,
                        key=key
                        )

            return error_response
        else:
            count = 0
            while count < 10:
                transaction, exception = self.create_transaction(
                    create_transaction_data)
                if transaction:
                    response_payload = {
                        "objectReference": trid,
                        "serverCorrelationId": server_correlation_id,
                        "status": "pending",
                        "notificationMethod": "callback",
                        "expiryTime": "",
                        "pollLimit": 0,
                        "error": None

                    }
                    logger.info("create_transaction_202",
                                status=status.HTTP_202_ACCEPTED,
                                trid=trid,
                                response_payload=response_payload
                                )
                    return Response(response_payload,
                                    status=status.HTTP_202_ACCEPTED
                                    )

                else:
                    if "trid" in exception:
                        error_message = "Unable to get a unique " \
                                        "transaction reference. Please retry"
                        error_key = "transaction_reference"
                    else:
                        error_message = exception
                        error_key = "serverCorrelationId"
                        break
                    trid = str(uuid.uuid4())
                    create_transaction_data['trid'] = trid
                    count += 1

            return send_error_response(
                message=error_message,
                key=error_key,
                status=status.HTTP_409_CONFLICT,
                value="Duplicate UUID"

            )

    @staticmethod
    def create_transaction(create_transaction_data):
        try:
            transaction = Transaction.objects.create(**create_transaction_data)
            logger.info("create_transaction_success",
                        trid=create_transaction_data.get('trid')
                        )
            return True, transaction
        except IntegrityError as e:
            exception = str(e).split("DETAIL:")[1]
            logger.info("create_transaction_duplicate_uuid",
                        exception=exception,
                        )
            return False, exception
