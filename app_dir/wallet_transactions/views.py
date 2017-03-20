from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from app_dir.customer_wallet_management.models import CustomerWallet
from .models import Transaction
from .serializers import TransactionSerializer

logger = get_logger("transactions")


def send_error_response(message="404",
                        key="trid",
                        value=None,
                        status=None,
                        ):
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


class TransactionList(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = (IsAdminUser,)


class TransactionRetrieve(generics.RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        """
        This view should return a list of all the purchases for
        the user as determined by the username portion of the URL.
        """
        transaction_id = self.kwargs['transactionReference']
        return Transaction.objects.filter(trid=transaction_id)


class GetTransaction(APIView):
    """
    This API retrieves a transaction given the transaction reference
    HTTP Method: GET
    URI: /api/v1/transactions/{transactionReference}
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    { //this is to be changed once correct
         "transaction": {
                    "reference": "transaction_reference",
                    "transaction_type": "transaction_type",
                    "amount": "transaction_amount",
                    "date": "transaction_date",
                    "status": "transaction_state",
                    "currency": "currency",
                    "serverCorrelationId: "serverCorrelationId"
                }
    }
    Error response: [404, 400, DATE header not supplied]
    {
        "errorCategory": "businessRule",
        "errorCode": "genericError",
        "errorDescription": "string",
        "errorDateTime": "string",
        "errorParameters": [
            {
                "key": key,
                "value": value
            }
        ]
    }
    """

    def get(self, request, transaction_reference):
        date = request.META.get("HTTP_DATE")
        if not date and not settings.DEBUG:
            logger.info("get_transaction_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        transaction_reference=transaction_reference,
                        key="DATE"
                        )
            return send_error_response(
                    message="DATE Header not supplied",
                    key="DATE",
                    status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transaction = Transaction.objects.get(trid=transaction_reference)
            transaction_state = transaction.state
            transaction_type = transaction.transaction_type
            transaction_amount = transaction.amount
            transaction_date = transaction.created_at.isoformat()
            transaction_currency = transaction.currency

            payload = {
                "transaction": {
                    "reference": transaction_reference,
                    "transaction_type": transaction_type,
                    "amount": transaction_amount,
                    "date": transaction_date,
                    "status": transaction_state,
                    "currency": transaction_currency
                }
            }
            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_transaction_200",
                        status=status.HTTP_200_OK,
                        trid=transaction_reference
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_transaction_404",
                        status=status.HTTP_404_NOT_FOUND,
                        trid=transaction_reference,
                        key="trid"
                        )

            return send_error_response(
                    message="Requested resource not available",
                    key="transaction_reference",
                    value=transaction_reference,
                    status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            logger.info("get_transaction_malformed_uuid",
                        status=status.HTTP_404_NOT_FOUND,
                        trid=transaction_reference,
                        key="trid"
                        )

            return send_error_response(
                    message="Malformed UUID",
                    key="transaction_reference",
                    value=transaction_reference,
                    status=status.HTTP_404_NOT_FOUND
            )


class GetTransactionState(APIView):
    """
    This API retrieves a transaction state given serverCorrelationId
    HTTP Method: GET
    URI: /api/v1/requeststates/{servierCorrelationId}
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    SERVERCORRELATIONID: serverCorrelationId (type: UUID)
    Success response:
    HTTP status code: 200
    {
        "reference": transaction_reference,
        "transaction_type": transaction_type,
        "amount": transaction_amount,
        "currency": "currency",
        "date": transaction_date,
        "status": transaction_state

    }
    Error response: [404, 400, DATE header not supplied]
    {
        "errorCategory": "businessRule",
        "errorCode": "genericError",
        "errorDescription": "string",
        "errorDateTime": "string",
        "errorParameters": [
            {
                "key": key,
                "value": value
            }
        ]
    }
    """

    def get(self, request, server_correlation_id):
        date = request.META.get("HTTP_DATE")
        if not date and not settings.DEBUG:
            logger.info("get_transaction_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        server_correlation_id=server_correlation_id,
                        key="DATE"
                        )
            return send_error_response(
                    message="DATE Header not supplied",
                    key="DATE",
                    status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transaction = Transaction.objects.get(
                    server_correlation_id=server_correlation_id)
            transaction_state = transaction.state
            transaction_type = transaction.transaction_type
            transaction_amount = transaction.amount
            transaction_date = transaction.created_at
            transaction_reference = transaction.trid
            transaction_currency = transaction.currency

            payload = {
                "reference": transaction_reference,
                "transaction_type": transaction_type,
                "amount": transaction_amount,
                "currency": transaction_currency,
                "date": transaction_date,
                "status": transaction_state,
                "serverCorrelationId": server_correlation_id,

            }
            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_transaction_state_200",
                        status=status.HTTP_200_OK,
                        serverCorrelationId=server_correlation_id
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_transaction_state_404",
                        status=status.HTTP_404_NOT_FOUND,
                        server_correlation_id=server_correlation_id,
                        key="server_correlation_id"
                        )

            return send_error_response(
                    message="Requested resource not available",
                    key="serverCorrelationId",
                    value=server_correlation_id,
                    status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            logger.info("get_transaction_state_malformed_uuid",
                        status=status.HTTP_400_BAD_REQUEST,
                        server_correlation_id=server_correlation_id,
                        key="serverCorrelationId"
                        )

            return send_error_response(
                    message="Malformed UUID string",
                    key="serverCorrelationId",
                    value=server_correlation_id,
                    status=status.HTTP_400_BAD_REQUEST
            )


class GetStatementByTransactionID(APIView):
    """
    This API fetches the customers last five transactions given the accountID
    HTTP Method: GET
    URI: /api/v1/statemententries/{transactionReference}
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
      "amount" : "451238",
      "currency" : "UGX",
      "displayType" : "transfer",
      "transactionStatus" : "checkSum value should be between 64 to 64",
      "descriptionText" : "",
      "requestDate" : "2016-12-15 09:27:16",
      "creationDate" : "",
      "modificationDate" : "",
      "transactionReference" : "TPXX000000055604",
      "transactionReceipt" : "",
      "debitParty" : [ {
        "key" : "msisdn",
        "value" : "+4491509874561"
      } ],
      "creditParty" : [ {
        "key" : "msisdn",
        "value" : "+25691508523697"
      } ]
    }
    Error response: [404, 400, account in inactive state,
                    DATE header not supplied]
    {
        "errorCategory": "businessRule",
        "errorCode": "genericError",
        "errorDescription": "string",
        "errorDateTime": "string",
        "errorParameters": [
            {
                "key": key,
                "value": value
            }
        ]
    }
    """

    def get(self, request, trid):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_statemententries_404",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        trid=trid,
                        key="DATE"
                        )
            return send_error_response(
                    message="DATE Header not supplied",
                    key="DATE",
                    value=trid,
                    status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transaction = Transaction.objects.get(trid=trid)
            debit_party_msisdn = CustomerWallet.objects.get(
                        wallet_id=transaction.destination.wallet_id).msisdn
            credit_party_msisdn = CustomerWallet.objects.get(
                        wallet_id=transaction.source.wallet_id).msisdn
            payload = ({
                        "amount": transaction.amount,
                        "currency": transaction.currency,
                        "displayType": transaction.transaction_type,
                        "transactionStatus": transaction.state,
                        "descriptionText": transaction.description_text,
                        "requestDate": transaction.request_date,
                        "creationDate": transaction.created_at,
                        "modificationDate": transaction.modified_at,
                        "transactionReference": transaction.trid,
                        "transactionReceipt": "",
                        "debitParty": [{
                            "key": "msisdn",
                            "value": debit_party_msisdn
                            }],
                        "creditParty": [{
                            "key": "msisdn",
                            "value": credit_party_msisdn
                            }]
                        })

            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_statemententries_200",
                        status=status.HTTP_200_OK,
                        key="trid",
                        trid=trid
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_stamententries_404",
                        status=status.HTTP_404_NOT_FOUND,
                        trid=trid,
                        key="trid"
                        )

            return send_error_response(
                    message="Requested resource not available",
                    key="trid",
                    value=trid,
                    status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            logger.info("get_stamententries_404",
                        status=status.HTTP_404_NOT_FOUND,
                        trid=trid,
                        key="trid"
                        )
            return send_error_response(
                    message="Malformed UUID",
                    key="trid",
                    value=trid,
                    status=status.HTTP_404_NOT_FOUND)
