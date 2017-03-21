import uuid
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import Http404
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.serializers import BatchTransactionSerializer

from .models import Transaction, BatchTransaction, BatchTransactionLookup
from .serializers import TransactionSerializer

logger = get_logger("transactions")


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


class GetBatchTransaction(APIView):
    """
    This API allows retrieving a bulk transaction given an ID
    """

    def get(self, request, batch_trid=None, state=None):
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

        kwargs = {}
        q_objects = Q()
        if batch_trid:
            kwargs['batch_transaction__batch_trid'] = batch_trid

        # todo-steve: feels a bit inelegant - look into refining this Q query
        if state:
            if state in ["completions", "rejections"]:
                if state == "rejections":
                    kwargs['transaction__state'] = \
                        Transaction.TRANSACTION_STATES[3][0]

                if state == "completions":
                    q_objects.add(
                        Q(transaction__state__exact=
                          Transaction.TRANSACTION_STATES[2][0]),
                        Q.OR
                    )
                    q_objects.add(
                        Q(transaction__state__exact=
                          Transaction.TRANSACTION_STATES[4][0]),
                        Q.OR
                    )
            else:
                logger.info(
                    "get_transaction_invalid_state",
                    status=status.HTTP_400_BAD_REQUEST,
                    state=state,
                    key="state"
                )

                return send_error_response(
                    message="Invalid State",
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
            print(q_objects)
            batch_transactions = BatchTransactionLookup.objects.filter(
                **kwargs
            ).filter(q_objects)

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
            amount = float(data["amount"])
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
                logger.info("create_transaction_balance",
                            balance=source_balance,
                            amount=amount,
                            source=str(source.wallet_id),
                            destination=str(destination.wallet_id)
                            )
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