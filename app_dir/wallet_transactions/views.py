from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer
from rest_framework.permissions import IsAdminUser
from structlog import get_logger

logger = get_logger("transactions")


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
                    "reference": transaction_reference,
                    "type": transaction_type,
                    "amount": transaction_amount,
                    "date": transaction_date,
                    "status": transaction_state
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
        if not date:
            logger.info("get_transaction_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        transaction_reference=transaction_reference,
                        key="DATE"
                        )
            return self.send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            transaction = Transaction.objects.get(trid=transaction_reference)
            transaction_state = transaction.state
            transaction_type = transaction.type
            transaction_amount = transaction.amount
            transaction_date = transaction.created_at

            payload = {
                "transaction": {
                    "reference": transaction_reference,
                    "type": transaction_type,
                    "amount": transaction_amount,
                    "date": transaction_date,
                    "status": transaction_state
                }
            }
            response = Response(data=payload,
                                content_type="application/json",
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

            return self.send_error_response(
                message="Requested resource not available",
                key="trid",
                value=transaction_reference,
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            logger.info("get_transaction_malformed_uuid",
                        status=status.HTTP_404_NOT_FOUND,
                        trid=transaction_reference,
                        key="trid"
                        )

            return self.send_error_response(
                message="Malformed UUID",
                key="trid",
                value=transaction_reference,
                status=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
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
                            content_type="application/json",
                            status=status
                            )
        return response
