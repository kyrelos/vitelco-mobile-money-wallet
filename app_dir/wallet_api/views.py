import uuid
from datetime import datetime

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
from app_dir.wallet_transactions.models import BatchTransaction, Transaction
from app_dir.wallet_transactions.serializers import BatchTransactionSerializer

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
            batch_transaction = BatchTransaction.objects.get(
                batch_trid=batch_trid
            )

            payload = {
                "transaction": {
                    "reference": batch_trid,
                    "merchant": model_to_dict(batch_transaction.merchant),
                    "created_at": batch_transaction.created_at,
                }
            }
            response = Response(
                data=payload, status=status.HTTP_200_OK
            )
            logger.info(
                "get_batch_transaction_200",
                status=status.HTTP_200_OK,
                batch_trid=batch_trid
            )
            return response

        except ObjectDoesNotExist:
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
    def get_object(self, pk):
        try:
            return BatchTransaction.objects.get(pk=pk)
        except BatchTransaction.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        bulk_transactions = BatchTransaction.objects.all()
        serializer = BatchTransactionSerializer(bulk_transactions, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BatchTransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("create_transaction_400",
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
                server_correlation_id=str(uuid.uuid4()),
                destination=destination,
                amount=amount,
                transaction_type=transaction_type
            )
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
                transaction = self.create_transaction(create_transaction_data)
                if transaction:
                    response_payload = {
                        "objectReference": trid,
                        "serverCorrelationId": "",
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
                    trid = str(uuid.uuid4())
                    create_transaction_data['trid'] = trid
                    count += 1

            return send_error_response(
                message="Unable to get a unique "
                        "transaction reference. Please retry",
                key="transaction_reference",
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
            return transaction
        except IntegrityError:
            logger.info("create_transaction_duplicate_uuid",
                        trid=create_transaction_data.get('trid')
                        )
            return False


