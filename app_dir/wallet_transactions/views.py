import json
import uuid
from datetime import datetime

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms import model_to_dict
from django.http import Http404, request
from django.db.models import Q
from requests import RequestException
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from structlog import get_logger

from app_dir.customer_wallet_management.models import CustomerWallet
from app_dir.wallet_transactions.serializers import BatchTransactionSerializer
from app_dir.wallet_transactions.tasks import process_transaction, \
    process_debit_mandate

from .models import Transaction, BatchTransaction, BatchTransactionLookup, \
    DebitMandate
from .serializers import TransactionSerializer, DebitMandateSerializer

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
    URI: /transactions/{transactionReference}
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
    URI: /requeststates/{serverCorrelationId}
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
    This API allows retrieving a bulk transaction given an ID.
    Will return a list of all transactions connected to that bulk transction

    HTTP Method: GET
    URI: /batchtransactions/

    Example request:
    /batchtransactions/0ca4f513-6728-4502-810c-f7132b4dc4f4

    Expected Response:
    {
        "reference": "0ca4f513-6728-4502-810c-f7132b4dc4f4",
        "transactions": [
            {
                "request_date": "2017-03-21",
                "currency": "KES",
                "trid": "e7815dcf-a2eb-4b92-bbdf-8f465125258a",
                "destination": 4,
                "state": "reversed",
                "transaction_type": "deposit",
                "source": 2,
                "amount": 10000,
                "server_correlation_id": "ea34585f-b153-456a-bf8d-b2134d3f7b0f",
                "description_text": null,
                "callback_url": null,
                "id": 1
            },
            {
                "request_date": "2017-03-21",
                "currency": "KES",
                "trid": "a898e9cb-a570-4611-ada0-1511906b5b0e",
                "destination": 4,
                "state": "completed",
                "transaction_type": "deposit",
                "source": 2,
                "amount": 1000,
                "server_correlation_id": "856cca14-b428-4ce2-9ef0-39413894851a",
                "description_text": null,
                "callback_url": null,
                "id": 2
            }
        ]
    }

    HTTP Method: GET
    URI: api/v1/batchtransactions/completions
    Returns transactions in "completed" or "rejected" state for a batch transaction

    Example request:
    api/v1/batchtransactions/0ca4f513-6728-4502-810c-f7132b4dc4f4/completions

    HTTP Method: GET
    URI: api/v1/batchtransactions/rejections
    Returns all transactions in "failed" state for a batch transaction

    Example request:
    api/v1/batchtransactions/0ca4f513-6728-4502-810c-f7132b4dc4f4/rejections

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
            batch_transactions = BatchTransactionLookup.objects.filter(
                q_objects, **kwargs
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


class CreateTransactions(APIView):
    """
      This API posts a transaction
      HTTP Method: POST
      URI: /transactions/

      Required HTTP Headers:
      DATE: todays date
      AUTHORIZATION: api-key
      CONTENT-TYPE: application/json
      X-CorrelationID: afc71b32-9a8d-4260-8cdc-c6f452b9b09f`

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
                    process_transaction.delay(trid)
                    logger.info("create_transaction_202",
                                status=status.HTTP_202_ACCEPTED,
                                trid=str(trid),
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
        except ObjectDoesNotExist as e:
            exception = str(e)
            logger.info("create_transaction_object_does_not_exist",
                        exception=exception,
                        )
            return False, exception
        except ValueError as e:
            exception = str(e)
            logger.info("create_transactions_value_error",
                        exception=exception,
                        )
            return False, exception


class BatchTransactions(APIView):
    """
    This API posts batch transactions
      HTTP Method: POST
      HTTP Headers:
    `Content-Type: application/json,
     Accept: application/json,
     Date: 21-03-2017,
     X-CorrelationID: afc71b32-9a8d-4260-8cdc-c6f452b9b09f`
      URI: /batchtransactions/

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
                try:
                    transaction_response = self.create_transaction(
                        json.dumps(data), request)
                    if transaction_response.status_code in (202, 201):
                        response_data = transaction_response.json()
                        trx = Transaction.objects.get(
                            trid=response_data["objectReference"])
                        batch_lookup = BatchTransactionLookup.objects.create(
                            batch_transaction=batch_trx,
                            transaction=trx)
                except RequestException as e:
                    logger.exception("create_transaction_exception",
                                     exception=e.message)
                except ValueError as e:
                    logger.exception("create_transaction_exception",
                                     exception=e.message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return_errors = dict(
                batch_transaction_errors=serializer.error_messages, )
            return Response(return_errors,
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create_transaction(self, data, request):
        server_correlation_id = str(uuid.uuid4())
        headers = {
            "X-CORRELATIONID": server_correlation_id,
            "Authorization": "api-key",
            "Content-type": "application/json"
        }
        logger.info("create_transaction_fxn", url=str(reverse(
            'create_transactions', request=request)))

        response = requests.post(reverse('create_transactions',
                                         request=request),
                                 data=data,
                                 headers=headers)

        logger.info("create_transaction_fxn_response",
                    response=str(response.text),
                    status_code=str(response.status_code))

        return response


class GetStatementByTransactionID(APIView):
    """
    This API fetches the customers last five transactions given the accountID
    HTTP Method: GET
    URI: /statemententries/{transactionReference}
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
                        trid=str(trid),
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
            from app_dir.customer_wallet_management.models import \
                CustomerWallet
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
                        trid=str(trid)
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_stamententries_404",
                        status=status.HTTP_404_NOT_FOUND,
                        trid=str(trid),
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
                        trid=str(trid),
                        key="trid"
                        )
            return send_error_response(
                message="Malformed UUID",
                key="trid",
                value=trid,
                status=status.HTTP_404_NOT_FOUND)


class DebitMandates(APIView):
    """
    This API posts debit mandates the calling msisdn is treated as the payer
    HTTP Headers:
    `Content-Type: application/json,
     Accept: application/json,
     Date: 21-03-2017,
     X-CorrelationID: afc71b32-9a8d-4260-8cdc-c6f452b9b09f`
      HTTP Method: POST
      URI: /accounts/msisdn/{msisdn}/debitmandates/

    ===== SAMPLE PAY LOAD ======
            {
            "requestdebitmandate":{
                "currency":"KES",
                "amount_limit":5000,
                "start_date":"2017-04-01 18:00:00",
                "end_date": "2018-03-31 18:00:00",
                "frequency_type": "monthspecificdate",
                "mandate_status": "active",
                "request_date": "2017-03-22 00:00:00",
                "number_of_payments":12,
                "debitParty": [
                {
                  "key": "msisdn",
                  "value": "254701814779"
                }
              ]
            }
        }
    """

    def post(self, request, msisdn, format=None):

        logger.info("debit_manage_with_msisdn", msisdn=msisdn)

        payer = CustomerWallet.objects.get(msisdn=msisdn)
        req = request.data["requestdebitmandate"]

        payee_msisdn = req["debitParty"][0]["value"]
        payee = CustomerWallet.objects.get(msisdn=payee_msisdn)

        debit_mandate_data = {
            "currency": req["currency"],
            "amount_limit": req["amount_limit"],
            "start_date": req["start_date"],
            "end_date": req["end_date"],
            "frequency_type": req["frequency_type"],
            "mandate_status": req["mandate_status"],
            "request_date": req["request_date"],
            "number_of_payments": req["number_of_payments"],
            "payer": payer,
            "payee": payee
        }

        debit_mandate = DebitMandate.objects.create(
            **debit_mandate_data)

        if debit_mandate.id:
            reponse_payload = {
                "mandateReference": str(debit_mandate.mandate_reference),
                "creationDate": str(debit_mandate.created_at),
                "modificationDate": str(debit_mandate.modified_at)
            }

            url = reverse("create_transactions",
                          request=request
                          )

            logger.info("debit_mandate_by_msisdn",
                        data=reponse_payload,
                        url=url
                        )
            process_debit_mandate(str(debit_mandate.mandate_reference), url)

            return Response(reponse_payload,
                            status=status.HTTP_201_CREATED)

        logger.info("debit_mandate_400", msisdn=msisdn)
        return Response("Error creating debit mandate",
                        status=status.HTTP_400_BAD_REQUEST)


class CreateDebitMandates(APIView):
    """
    This API posts debit mandates the calling msisdn is treated as the payer
      HTTP Method: POST
      HTTP Headers:
    `Content-Type: application/json,
     Accept: application/json,
     Date: 21-03-2017,
     X-CorrelationID: afc71b32-9a8d-4260-8cdc-c6f452b9b09f`
      URI: /accounts/{accountId}/debitmandates/

    ===== SAMPLE PAY LOAD ======
            {
            "requestdebitmandate":{
                "currency":"KES",
                "amount_limit":5000,
                "start_date":"2017-04-01 18:00:00",
                "end_date": "2018-03-31 18:00:00",
                "frequency_type": "monthspecificdate",
                "mandate_status": "active",
                "request_date": "2017-03-22 00:00:00",
                "number_of_payments":12,
                "debitParty": [
                {
                  "key": "msisdn",
                  "value": "254701814779"
                }
              ]
            }
        }
    """
    def post(self, request, account_id, format=None):
        account = CustomerWallet.objects.filter(wallet_id=account_id)
        req = request.data["requestdebitmandate"]

        payee_msisdn = req["debitParty"][0]["value"]
        payee = CustomerWallet.objects.get(msisdn=payee_msisdn)

        debit_mandate_data = {
            "account_id": account,
            "currency": req["currency"],
            "amount_limit": req["amount_limit"],
            "start_date": req["start_date"],
            "end_date": req["end_date"],
            "frequency_type": req["frequency_type"],
            "mandate_status": req["mandate_status"],
            "request_date": req["request_date"],
            "number_of_payments": req["number_of_payments"],
            "payer": account,
            "payee": payee
        }

        debit_mandate = DebitMandate.objects.create(
            **debit_mandate_data)

        if debit_mandate.id:
            reponse_payload = {
                "mandateReference": str(debit_mandate.mandate_reference),
                "creationDate": str(debit_mandate.created_at),
                "modificationDate": str(debit_mandate.modified_at)
            }

            url = reverse("create_transactions",
                          request=request
                          )

            logger.info("debit_mandate_by_msisdn",
                        data=reponse_payload,
                        url=url
                        )
            process_debit_mandate.delay(str(debit_mandate.mandate_reference),
                                      url)

            return Response(reponse_payload,
                            status=status.HTTP_201_CREATED)

        logger.info("debit_mandate_400", account_id=account_id)
        return Response("Error creating debit mandate",
                        status=status.HTTP_400_BAD_REQUEST)
