import uuid
from datetime import datetime

from django.db import IntegrityError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.models import BatchTransaction, Transaction
from app_dir.wallet_transactions.serializers import BatchTransactionSerializer


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
                "Create Transaction": reverse(
                    "create_transactions",
                    request=request
                )

            },
            "BatchTransactions": {
                "Create batch transactions": reverse(
                        "batchtransactions", request=request
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
        try:
            data = request.data
            trid = uuid.uuid4()
            source_msisdn = data["debitParty"][0]["value"]
            source = CustomerWallet.objects.get(msisdn=source_msisdn)
            destination_msisdn = data["creditParty"][0]["value"]
            destination = CustomerWallet.objects.get(msisdn=destination_msisdn)
            amount = data["amount"]
            transaction_type = data["type"]
            create_transaction_data = dict(
                trid=trid,
                source=source,
                destination=destination,
                amount=amount,
                type=transaction_type
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

            return error_response
        else:
            duplicate_transaction = True
            count = 0
            while duplicate_transaction:
                transaction = self.create_transaction(create_transaction_data)
                if transaction:
                    break
                else:
                    trid, create_transaction_data['trid'] = uuid.uuid4()
                    count += 1

            response_payload = {
                "objectReference": trid,
                "serverCorrelationId": "",
                "status": "pending",
                "notificationMethod": "callback",
                "expiryTime": "",
                "pollLimit": 0,
                "error": None

            }
            return Response(response_payload,
                            status=status.HTTP_202_ACCEPTED
                            )

    @staticmethod
    def create_transaction(create_transaction_data):
        try:
            transaction = Transaction.objects.create(**create_transaction_data)
            return transaction
        except IntegrityError:
            return False


