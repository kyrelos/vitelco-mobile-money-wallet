import json
import uuid
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

import requests
from django.db import IntegrityError
from requests import RequestException
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from structlog import get_logger
from app_dir.bill_management.models import Bill
from app_dir.customer_wallet_management.models import CustomerWallet

logger = get_logger("bills")


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


class CreateBill(APIView):
    """
    This API creates a bill object

    URL: /bills/

    HTTP Headers:
    `Content-Type: application/json,
     Accept: application/json,
     Date: 21-03-2017,
     X-CorrelationID: afc71b32-9a8d-4260-8cdc-c6f452b9b09f`

    Example payload:
    {
        "currency": "KES",
        "amountDue": "10000",
        "minAmountDue": "1",
        "dueDate": "2017-02-28 16:00:00",
        "debitParty": [
        {
        "key": "msisdn",
        "value": "+4491509874561"
        }],
        "creditParty": [
        {
        "key": "msisdn",
        "value": "+25691508523697"
        }],
        "billDescription": "Bill description"
        }


    Example response:
    {
        "bill_reference": "afc71b32-9a8d-4260-8cdc-c6f452b9b09g"
    }
    """

    def post(self, request):

        try:
            data = request.data
            biller_msisdn = data["creditParty"][0]["value"]
            biller = CustomerWallet.objects.get(msisdn=biller_msisdn)
            billee_msisdn = data["debitParty"][0]["value"]
            billee = CustomerWallet.objects.get(msisdn=billee_msisdn)
            amount_due = data["amountDue"]
            currency = data["currency"]
            due_date = data["dueDate"]
            bill_description = data.get('billDescription')
            min_amount_due = data.get('minAmountDue')

            create_bill_data = dict(
                biller=biller,
                billee=billee,
                amount_due=amount_due,
                currency=currency,
                due_date=due_date,
                bill_description=bill_description,
                min_amount_due=min_amount_due,
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

            logger.info("create_bill_400",
                        status=status.HTTP_400_BAD_REQUEST,
                        key=key
                        )

            return error_response
        except ObjectDoesNotExist as e:
            exception = str(e)
            logger.info("create_bill_object_does_not_exist",
                        exception=exception,
                        )
            error_message = "MSISDN does not exist"
            key = "CreditParty | DebitParty"
            value = e.message
            status_code = status.HTTP_400_BAD_REQUEST
            error_response = send_error_response(
                message=error_message,
                key=key,
                value=value,
                status=status_code
            )

            logger.info("create_bill_400",
                        status=status.HTTP_400_BAD_REQUEST,
                        key=key
                        )

            return error_response
        else:
            created, bill = self.create_bill(create_bill_data)
            if bill:
                bill_reference = str(bill.bill_reference)
                response_payload = {
                    "billReference": bill_reference,

                }
                logger.info("create_bill_201",
                            status=status.HTTP_201_CREATED,
                            bill_reference=bill_reference,
                            response_payload=response_payload
                            )
            return Response(response_payload,
                            status=status.HTTP_201_CREATED
                            )

    @staticmethod
    def create_bill(create_bill_data):
        try:
            transaction = Bill.objects.create(**create_bill_data)
            logger.info("create_bill_success",
                        bill_reference=create_bill_data.get('bill_reference')
                        )
            return True, transaction
        except IntegrityError as e:
            exception = str(e).split("DETAIL:")[1]
            logger.info("create_bill_duplicate_uuid",
                        exception=exception,
                        )
            return False, exception

        except ObjectDoesNotExist as e:
            exception = str(e)
            logger.info("create_bill_object_does_not_exist",
                        exception=exception,
                        )
            return False, exception


class CreateBillPaymentByMsisdn(APIView):
    """
    This API creates a bill payment

    URI: /accounts/msisdn/{msisdn}/bills/{billReference}/payments

    HTTP Headers:
    `Content-Type: application/json,
     Accept: application/json,
     Date: 21-03-2017,
     X-CorrelationID: afc71b32-9a8d-4260-8cdc-c6f452b9b09f`

    Example payload:
    {
        "currency": "KES",
        "paidamount": "10000",
    }


    Example response:
   {
  "status": "success",
  "bill_reference": "b8f8f652-6ab0-4789-8c36-c0bfa0087031",
  "serverCorrelationId": "c7717afc-610d-426d-8884-6816bcb6ad1b"
}

    """

    def post(self, request, msisdn, bill_reference):

        logger.info("create_bill_payments_using_msisdn",
                    msisdn=msisdn,
                    bill_reference=bill_reference
                    )

        try:

            billee = CustomerWallet.objects.get(msisdn=msisdn)
            bill = Bill.objects.get(bill_reference=bill_reference)

            timestamp = timezone.now()

            url = reverse("create_transactions", request=request)

            if billee == bill.billee and bill.bill_status != "paid":

                debit_party_msisdn = billee.msisdn
                credit_party_msisdn = bill.biller.msisdn

                currency = request.data["currency"]
                amount = request.data["paidamount"]

                transaction_payload = {
                    "requestingOrganisationTransactionReference": "MWCAPIWorkshop001",
                    "debitParty": [
                        {"value": debit_party_msisdn,
                         "key": "msisdn"}
                    ],
                    "currency": currency,
                    "amount": amount,
                    "requestDate": timestamp.isoformat(), "creditParty": [
                        {"value": credit_party_msisdn,
                         "key": "msisdn"}
                    ],
                    "type": "transfer"
                }

                try:
                    server_correlation_id = str(uuid.uuid4())
                    headers = {
                        "X-CORRELATIONID": server_correlation_id,
                        "Authorization": "api-key",
                        "Content-type": "application/json"
                    }
                    logger.info("create_bill_payment_request",
                                url=url,
                                payload=transaction_payload)

                    response = requests.post(url,
                                             data=json.dumps(
                                                 transaction_payload),
                                             headers=headers
                                             )
                    if response.status_code in (202, 201):
                        bill.bill_status = "paid"
                        bill.save()

                        logger.info("create_bill_payment_response",
                                    response=str(response.text),
                                    status_code=str(response.status_code))

                        response_payload = {
                            "serverCorrelationId": str(server_correlation_id),
                            "bill_reference": bill_reference,
                            "status": "success"
                        }

                        return Response(response_payload,
                                        status=status.HTTP_201_CREATED
                                        )

                except RequestException as e:
                    logger.exception("create_bill_payment_exception",
                                     exception=e.message)

                except ValueError as e:
                    logger.exception("create_bill_payment_exception",
                                     exception=e.message)

            else:
                response_payload = {
                    "bill_reference": bill_reference,
                    "status": "failed",
                    "message": "bill already paid"
                }

                return Response(response_payload,
                                status=status.HTTP_200_OK
                                )
        except ValueError as e:
            logger.exception("create_bill_payment_exception",
                             exception=e.message)

            return send_error_response(message=e.message,
                                       key="bill_reference",
                                       value=bill_reference,
                                       status=status.HTTP_400_BAD_REQUEST
                                       )
