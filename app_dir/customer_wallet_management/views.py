from datetime import datetime
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from app_dir.wallet_transactions.models import Transaction, DebitMandate
from .models import CustomerWallet
from .serializers import CustomerWalletSerializer

logger = get_logger("accounts")


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


class CustomerWalletViewSet(APIView):
    def get_object(self, pk):
        try:
            return CustomerWallet.objects.get(pk=pk)
        except CustomerWallet.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        accounts = CustomerWallet.objects.all()
        serializer = CustomerWalletSerializer(accounts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CustomerWalletSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        account = self.get_object(pk)
        serializer = CustomerWalletSerializer(account, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        account = self.get_object(pk)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetAccountStatusByMsisdn(APIView):
    """
      This API retrieves the customer's account status given a msisdn
      HTTP Method: GET
      URI: /accounts/msisdn/{msisdn}/status/

      Required HTTP Headers:
      DATE: todays date
      AUTHORIZATION: api-key
      CONTENT-TYPE: application/json

      Success response:
      HTTP status code: 200
      {
        "status" : "Active",
        "subStatus" : "Terrapay - Active",
        "lei" : "Terrapay Ltd"
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

    def get(self, request, msisdn):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountstatus_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)
            account_status = account.status
            payload = {
                "status": account_status,
                "subStatus": "",
                "lei": ""}

            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_accountstatus_200",
                        status=status.HTTP_200_OK,
                        msisdn=msisdn
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_accountstatus_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )
            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND)


class GetAccountStatusByAccountId(APIView):
    """
      This API retrieves the customer's account status given a UUID
      HTTP Method: GET
      URI: /accounts/{uuid}/status/

      Required HTTP Headers:
      DATE: todays date
      AUTHORIZATION: api-key
      CONTENT-TYPE: application/json

      Success response:
      HTTP status code: 200
      {
        "status" : "Active",
        "subStatus" : "Terrapay - Active",
        "lei" : "Terrapay Ltd"
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

    def get(self, request, wallet_id):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountstatus_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=str(wallet_id),
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = CustomerWallet.objects.get(wallet_id=wallet_id)
            account_status = account.status
            payload = {
                "status": account_status,
                "subStatus": "",
                "lei": ""}

            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_accountstatus_200",
                        status=status.HTTP_200_OK,
                        wallet_id=str(wallet_id)
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_accountstatus_404",
                        status=status.HTTP_404_NOT_FOUND,
                        wallet_id=str(wallet_id),
                        key="wallet_id"
                        )
            return send_error_response(
                message="Requested resource not available",
                key="wallet_id",
                value=wallet_id,
                status=status.HTTP_404_NOT_FOUND)

        except ValueError:
            logger.info("get_accountstatus_400",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=str(wallet_id),
                        key="wallet_id"
                        )
            return send_error_response(
                message="Malformed UUID",
                key="wallet_id",
                value=wallet_id,
                status=status.HTTP_400_BAD_REQUEST)


class GetAccountNameByMsisdn(APIView):
    """
    This API retrieves the customers name details given a msisdn
    HTTP Method: GET
    URI: /accounts/msisdn/{msisdn}/accountname/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "name": {
            "title": "",
            "firstName": first_name,
            "middleName": "",
            "lastName": "",
            "fullName": "",
            "nativeName": ""
        },
        "status": "",
        "lei": ""
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

    def get(self, request, msisdn):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountname_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)
            first_name = account.name
            account_status = account.status
            if account_status == CustomerWallet.active:
                payload = {
                    "name": {
                        "title": "",
                        "firstName": first_name,
                        "middleName": "",
                        "lastName": "",
                        "fullName": "",
                        "nativeName": ""
                    },
                    "status": "",
                    "lei": ""
                }
                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accountname_200",
                            status=status.HTTP_200_OK,
                            msisdn=msisdn
                            )
                return response
            else:
                logger.info("get_accountname_404",
                            status=status.HTTP_404_NOT_FOUND,
                            msisdn=msisdn,
                            key="msisdn_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="msisdn",
                    value=msisdn,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_accountname_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND
            )


class GetAccountNameByAccountId(APIView):
    """
    This API retrieves the customers name details given a account_id

    HTTP Method: GET
    URI: /accounts/{account_id}/accountname/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "name": {
            "title": "",
            "firstName": first_name,
            "middleName": "",
            "lastName": "",
            "fullName": "",
            "nativeName": ""
        },
        "status": "",
        "lei": ""
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

    def get(self, request, account_id):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountname_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        account_id=account_id,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = CustomerWallet.objects.get(wallet_id=account_id)
            first_name = account.name
            account_status = account.status
            if account_status == CustomerWallet.active:
                payload = {
                    "name": {
                        "title": "",
                        "firstName": first_name,
                        "middleName": "",
                        "lastName": "",
                        "fullName": "",
                        "nativeName": ""
                    },
                    "status": "",
                    "lei": ""
                }
                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accountname_200",
                            status=status.HTTP_200_OK,
                            account_id=str(account_id)
                            )
                return response
            else:
                logger.info("get_accountname_404",
                            status=status.HTTP_404_NOT_FOUND,
                            account_id=str(account_id),
                            key="msisdn_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="account_id",
                    value=account_id,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_accountname_404",
                        status=status.HTTP_404_NOT_FOUND,
                        account_id=str(account_id),
                        key="account_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="account_id",
                value=account_id,
                status=status.HTTP_404_NOT_FOUND
            )


class AccountBalanceByMsisdn(APIView):
    """
    This API fetches the customers balance details given a msisdn
    HTTP Method: GET
    URI: /accounts/msisdn/{msisdn}/balance/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "currentBalance": "5000",
        "availableBalance": "5000",
        "reservedBalance": "200",
        "unclearedBalance": "100",
        "currency": "KES",
        "status": "active/inactive"
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

    def get(self, request, msisdn):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountbalancebymsisdn_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=msisdn,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)
            account_status = account.status
            if account_status == CustomerWallet.active:
                payload = {
                    'currentBalance': account.get_actual_balance(),
                    'availableBalance': account.get_available_balance(),
                    'reservedBalance': account.get_reserved_balance(),
                    'unclearedBalance': account.get_uncleared_balance(),
                    'currency': 'KES',
                    'status': 'active'
                }
                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accountbalancebymsisdn_200",
                            status=status.HTTP_200_OK,
                            key="msisdn",
                            msisdn=msisdn
                            )
                return response
            else:
                logger.info("get_accountbalancebymsisdn_404",
                            status=status.HTTP_404_NOT_FOUND,
                            msisdn=msisdn,
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="msisdn",
                    value=msisdn,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_accountbalancebymsisdn_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND
            )


class AccountBalanceByAccountId(APIView):
    """
    This API fetches the customers balance details given an account_id
    HTTP Method: GET
    URI: /accounts/{account_id}/balance/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "currentBalance": "5000",
        "availableBalance": "5000",
        "reservedBalance": "200",
        "unclearedBalance": "100",
        "currency": "KES",
        "status": "active/inactive"
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

    def get(self, request, account_id):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountbalancebyaccountid_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        account_id=str(account_id),
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                status=status.HTTP_400_BAD_REQUEST
            )

        if not is_valid_uuid(account_id):
            logger.info("get_accountbalancebyaccountid_400",
                        message="account_id invalid",
                        status=status.HTTP_400_BAD_REQUEST,
                        account_id=str(account_id),
                        key="account_id"
                        )
            return send_error_response(
                message="account_id invalid",
                key="account_id",
                value=account_id,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the account for this account id
        try:
            account = CustomerWallet.objects.get(wallet_id=account_id)
            account_status = account.status
            if account_status == CustomerWallet.active:
                payload = {
                    'currentBalance': account.get_actual_balance(),
                    'availableBalance': account.get_available_balance(),
                    'reservedBalance': account.get_reserved_balance(),
                    'unclearedBalance': account.get_uncleared_balance(),
                    'currency': 'KES',
                    'status': 'active'
                }
                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accountbalancebyaccountid_200",
                            status=status.HTTP_200_OK,
                            key="account_id",
                            account_id=str(account_id)
                            )
                return response
            else:
                logger.info("get_accountbalancebyaccountid_404",
                            status=status.HTTP_404_NOT_FOUND,
                            account_id=str(account_id),
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="account_id",
                    value=account_id,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_accountbalancebyaccountid_404",
                        status=status.HTTP_404_NOT_FOUND,
                        account_id=str(account_id),
                        key="account_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="account_id",
                value=account_id,
                status=status.HTTP_404_NOT_FOUND
            )


class AccountTransactionsByMsisdn(APIView):
    """
    This API fetches the customers transactions given an msisdn
    HTTP Method: GET
    URI: /accounts/msisdn/{msisdn}/transactions/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    [ {
  "amount" : "451238",
  "currency" : "UGX",
  "type" : "transfer",
  "subType" : "",
  "descriptionText" : "",
  "requestDate" : "2016-12-15 09:27:16",
  "requestingOrganisationTransactionReference" : "",
  "oneTimeCode" : "",
  "geoCode" : "",
  "debitParty" : [ {
    "key" : "msisdn",
    "value" : "+4491509874561"
  }, {
    "key" : "bankaccountno",
    "value" : "2097123912831"
  } ],
  "creditParty" : [ {
    "key" : "msisdn",
    "value" : "+25691508523697"
  } ],
  "senderKyc" : {
    "nationality" : "UK",
    "dateOfBirth" : "",
    "occupation" : "",
    "employerName" : "",
    "contactPhone" : "+4491509874561",
    "gender" : "",
    "idDocument" : [ {
      "idType" : "VOTER_CARD",
      "idNumber" : "13321115521",
      "issueDate" : "",
      "expiryDate" : "",
      "issuer" : "",
      "issuerPlace" : "",
      "issuerCountry" : "",
      "otherIdDescription" : ""
    } ],
    "postalAddress" : {
      "addressLine1" : "49 , park street",
      "addressLine2" : "",
      "addressLine3" : "",
      "city" : "",
      "stateProvince" : "",
      "postalCode" : "",
      "country" : ""
    },
    "subjectName" : {
      "title" : "",
      "firstName" : "Einstein ",
      "middleName" : "",
      "lastName" : "BELA",
      "fullName" : "",
      "nativeName" : ""
    },
    "emailAddress" : "",
    "birthCountry" : ""
  },
  "recipientKyc" : {
    "nationality" : "",
    "dateOfBirth" : "",
    "occupation" : "",
    "employerName" : "",
    "contactPhone" : "",
    "gender" : "",
    "idDocument" : [ {
      "idType" : "",
      "idNumber" : "",
      "issueDate" : "",
      "expiryDate" : "",
      "issuer" : "",
      "issuerPlace" : "",
      "issuerCountry" : "",
      "otherIdDescription" : ""
    } ],
    "postalAddress" : {
      "addressLine1" : "",
      "addressLine2" : "",
      "addressLine3" : "",
      "city" : "",
      "stateProvince" : "",
      "postalCode" : "",
      "country" : ""
    },
    "subjectName" : {
      "title" : "",
      "firstName" : "",
      "middleName" : "",
      "lastName" : "",
      "fullName" : "",
      "nativeName" : ""
    },
    "emailAddress" : "",
    "birthCountry" : ""
  },
  "originalTransactionReference" : "",
  "servicingIdentity" : "",
  "requestingLei" : "",
  "receivingLei" : "",
  "metadata" : [ {
    "key" : "",
    "value" : ""
  } ],
  "transactionStatus" : "Remit Success",
  "creationDate" : "",
  "modificationDate" : "",
  "transactionReference" : "TPGS000000055601",
  "transactionReceipt" : "",
  "internationalTransferInformation" : {
    "originCountry" : "",
    "quotationReference" : "QR8436833",
    "quoteId" : "QT037f8mIomN4YJb1",
    "receivingCountry" : "",
    "remittancePurpose" : "1",
    "relationshipSender" : "",
    "deliveryMethod" : "directtoaccount",
    "senderBlockingReason" : "",
    "recipientBlockingReason" : ""
  }
} ]
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

    def get(self, request, msisdn):
        date = request.META.get("HTTP_DATE")
        limit = request.POST.get("LIMIT", 50)
        offset = request.POST.get("OFFSET", 0)
        from_date = request.POST.get("FROMDATETIME", None)
        to_date = request.POST.get("TODATETIME", None)
        if not date:
            logger.info("get_accounttransactionsbymsisdn_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=msisdn,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)
            if from_date and to_date:
                transactions = (account.transaction_source.all().
                                filter(created_at__gte=from_date).
                                filter(created_at__lte=to_date) | account.
                                transaction_destination.all().
                                filter(created_at__gte=from_date).
                                filter(created_at__lte=to_date))[offset:limit]
            elif from_date:
                transactions = (account.transaction_source.all().
                                filter(created_at__gte=from_date) | account.
                                transaction_destination.all().
                                filter(created_at__gte=from_date)
                                )[offset:limit]
            elif to_date:
                transactions = (account.transaction_source.all().
                                filter(created_at__lte=to_date) | account.
                                transaction_destination.all().
                                filter(created_at__lte=to_date))[offset:limit]
            else:
                transactions = (account.transaction_source.all() | account.
                                transaction_destination.all())[offset:limit]

            account_status = account.status
            payload = []
            if account_status == CustomerWallet.active:

                for transaction in transactions:
                    debit_party = CustomerWallet.objects.get(
                        wallet_id=transaction.destination.wallet_id)
                    credit_party = CustomerWallet.objects.get(
                        wallet_id=transaction.source.wallet_id)

                    payload.append({
                        "amount": transaction.amount,
                        "currency": transaction.currency,
                        "type": transaction.transaction_type,
                        "subType": "",
                        "descriptionText": "",
                        "requestDate": "",
                        "requestingOrganisationTransactionReference": "",
                        "oneTimeCode": "",
                        "geoCode": "",
                        "debitParty": [{
                            "key": "msisdn",
                            "value": credit_party.msisdn
                        }, {
                            "key": "bankaccountno",
                            "value": ""
                        }],
                        "creditParty": [{
                            "key": "msisdn",
                            "value": debit_party.msisdn
                        }],
                        "senderKyc": {
                            "nationality": "",
                            "dateOfBirth": "",
                            "occupation": "",
                            "employerName": "",
                            "contactPhone": credit_party.msisdn,
                            "gender": "",
                            "idDocument": [{
                                "idType": "",
                                "idNumber": "",
                                "issueDate": "",
                                "expiryDate": "",
                                "issuer": "",
                                "issuerPlace": "",
                                "issuerCountry": "",
                                "otherIdDescription": ""
                            }],
                            "postalAddress": {
                                "addressLine1": "",
                                "addressLine2": "",
                                "addressLine3": "",
                                "city": "",
                                "stateProvince": "",
                                "postalCode": "",
                                "country": ""
                            },
                            "subjectName": {
                                "title": "",
                                "firstName": credit_party.name,
                                "middleName": "",
                                "lastName": "",
                                "fullName": "",
                                "nativeName": ""
                            },
                            "emailAddress": "",
                            "birthCountry": ""
                        },
                        "recipientKyc": {
                            "nationality": "",
                            "dateOfBirth": "",
                            "occupation": "",
                            "employerName": "",
                            "contactPhone": "",
                            "gender": "",
                            "idDocument": [{
                                "idType": "",
                                "idNumber": "",
                                "issueDate": "",
                                "expiryDate": "",
                                "issuer": "",
                                "issuerPlace": "",
                                "issuerCountry": "",
                                "otherIdDescription": ""
                            }],
                            "postalAddress": {
                                "addressLine1": "",
                                "addressLine2": "",
                                "addressLine3": "",
                                "city": "",
                                "stateProvince": "",
                                "postalCode": "",
                                "country": ""
                            },
                            "subjectName": {
                                "title": "",
                                "firstName": debit_party.name,
                                "middleName": "",
                                "lastName": "",
                                "fullName": "",
                                "nativeName": ""
                            },
                            "emailAddress": "",
                            "birthCountry": ""
                        },
                        "originalTransactionReference": "",
                        "servicingIdentity": "",
                        "requestingLei": "",
                        "receivingLei": "",
                        "metadata": [{
                            "key": "",
                            "value": ""
                        }],
                        "transactionStatus": transaction.state,
                        "creationDate": transaction.created_at,
                        "modificationDate": transaction.modified_at,
                        "transactionReference": "",
                        "transactionReceipt": "",
                        "internationalTransferInformation": {
                            "originCountry": "",
                            "quotationReference": "",
                            "quoteId": "",
                            "receivingCountry": "",
                            "remittancePurpose": "1",
                            "relationshipSender": "",
                            "deliveryMethod": "",
                            "senderBlockingReason": "",
                            "recipientBlockingReason": ""
                        }
                    })

                # payload.append({
                #     'test': test
                # })
                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accounttransactionsbymsisdn_200",
                            status=status.HTTP_200_OK,
                            key="msisdn",
                            msisdn=msisdn
                            )
                return response
            else:
                logger.info("get_accounttransactionsbymsisdn_404",
                            status=status.HTTP_404_NOT_FOUND,
                            msisdn=msisdn,
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="msisdn",
                    value=msisdn,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_accounttransactionsbymsisdn_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND
            )


class AccountTransactionsByAccountId(APIView):
    """
    This API fetches the customers transactions given an msisdn
    HTTP Method: GET
    URI: /accounts/{accountId}/transactions/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    [ {
  "amount" : "451238",
  "currency" : "UGX",
  "type" : "transfer",
  "subType" : "",
  "descriptionText" : "",
  "requestDate" : "2016-12-15 09:27:16",
  "requestingOrganisationTransactionReference" : "",
  "oneTimeCode" : "",
  "geoCode" : "",
  "debitParty" : [ {
    "key" : "msisdn",
    "value" : "+4491509874561"
  }, {
    "key" : "bankaccountno",
    "value" : "2097123912831"
  } ],
  "creditParty" : [ {
    "key" : "msisdn",
    "value" : "+25691508523697"
  } ],
  "senderKyc" : {
    "nationality" : "UK",
    "dateOfBirth" : "",
    "occupation" : "",
    "employerName" : "",
    "contactPhone" : "+4491509874561",
    "gender" : "",
    "idDocument" : [ {
      "idType" : "VOTER_CARD",
      "idNumber" : "13321115521",
      "issueDate" : "",
      "expiryDate" : "",
      "issuer" : "",
      "issuerPlace" : "",
      "issuerCountry" : "",
      "otherIdDescription" : ""
    } ],
    "postalAddress" : {
      "addressLine1" : "49 , park street",
      "addressLine2" : "",
      "addressLine3" : "",
      "city" : "",
      "stateProvince" : "",
      "postalCode" : "",
      "country" : ""
    },
    "subjectName" : {
      "title" : "",
      "firstName" : "Einstein ",
      "middleName" : "",
      "lastName" : "BELA",
      "fullName" : "",
      "nativeName" : ""
    },
    "emailAddress" : "",
    "birthCountry" : ""
  },
  "recipientKyc" : {
    "nationality" : "",
    "dateOfBirth" : "",
    "occupation" : "",
    "employerName" : "",
    "contactPhone" : "",
    "gender" : "",
    "idDocument" : [ {
      "idType" : "",
      "idNumber" : "",
      "issueDate" : "",
      "expiryDate" : "",
      "issuer" : "",
      "issuerPlace" : "",
      "issuerCountry" : "",
      "otherIdDescription" : ""
    } ],
    "postalAddress" : {
      "addressLine1" : "",
      "addressLine2" : "",
      "addressLine3" : "",
      "city" : "",
      "stateProvince" : "",
      "postalCode" : "",
      "country" : ""
    },
    "subjectName" : {
      "title" : "",
      "firstName" : "",
      "middleName" : "",
      "lastName" : "",
      "fullName" : "",
      "nativeName" : ""
    },
    "emailAddress" : "",
    "birthCountry" : ""
  },
  "originalTransactionReference" : "",
  "servicingIdentity" : "",
  "requestingLei" : "",
  "receivingLei" : "",
  "metadata" : [ {
    "key" : "",
    "value" : ""
  } ],
  "transactionStatus" : "Remit Success",
  "creationDate" : "",
  "modificationDate" : "",
  "transactionReference" : "TPGS000000055601",
  "transactionReceipt" : "",
  "internationalTransferInformation" : {
    "originCountry" : "",
    "quotationReference" : "QR8436833",
    "quoteId" : "QT037f8mIomN4YJb1",
    "receivingCountry" : "",
    "remittancePurpose" : "1",
    "relationshipSender" : "",
    "deliveryMethod" : "directtoaccount",
    "senderBlockingReason" : "",
    "recipientBlockingReason" : ""
  }
} ]
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

    def get(self, request, account_id):
        date = request.META.get("HTTP_DATE")
        limit = request.POST.get("LIMIT", 50)
        offset = request.POST.get("OFFSET", 0)
        from_date = request.POST.get("FROMDATETIME", None)
        to_date = request.POST.get("TODATETIME", None)
        if not date:
            logger.info("get_accounttransactionsbyaccount_id_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=str(account_id),
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=account_id,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(wallet_id=account_id)
            if from_date and to_date:
                transactions = (account.transaction_source.all().
                                filter(created_at__gte=from_date).
                                filter(created_at__lte=to_date) | account.
                                transaction_destination.all().
                                filter(created_at__gte=from_date).
                                filter(created_at__lte=to_date))[offset:limit]
            elif from_date:
                transactions = (account.transaction_source.all().
                                filter(created_at__gte=from_date) | account.
                                transaction_destination.all().
                                filter(created_at__gte=from_date)
                                )[offset:limit]
            elif to_date:
                transactions = (account.transaction_source.all().
                                filter(created_at__lte=to_date) | account.
                                transaction_destination.all().
                                filter(created_at__lte=to_date))[offset:limit]
            else:
                transactions = (account.transaction_source.all() | account.
                                transaction_destination.all())[offset:limit]

            account_status = account.status
            payload = []
            if account_status == CustomerWallet.active:

                for transaction in transactions:
                    debit_party = CustomerWallet.objects.get(
                        wallet_id=transaction.destination.wallet_id)
                    credit_party = CustomerWallet.objects.get(
                        wallet_id=transaction.source.wallet_id)

                    payload.append({
                        "amount": transaction.amount,
                        "currency": transaction.currency,
                        "type": transaction.transaction_type,
                        "subType": "",
                        "descriptionText": "",
                        "requestDate": "",
                        "requestingOrganisationTransactionReference": "",
                        "oneTimeCode": "",
                        "geoCode": "",
                        "debitParty": [{
                            "key": "msisdn",
                            "value": credit_party.msisdn
                        }, {
                            "key": "bankaccountno",
                            "value": ""
                        }],
                        "creditParty": [{
                            "key": "msisdn",
                            "value": debit_party.msisdn
                        }],
                        "senderKyc": {
                            "nationality": "",
                            "dateOfBirth": "",
                            "occupation": "",
                            "employerName": "",
                            "contactPhone": credit_party.msisdn,
                            "gender": "",
                            "idDocument": [{
                                "idType": "",
                                "idNumber": "",
                                "issueDate": "",
                                "expiryDate": "",
                                "issuer": "",
                                "issuerPlace": "",
                                "issuerCountry": "",
                                "otherIdDescription": ""
                            }],
                            "postalAddress": {
                                "addressLine1": "",
                                "addressLine2": "",
                                "addressLine3": "",
                                "city": "",
                                "stateProvince": "",
                                "postalCode": "",
                                "country": ""
                            },
                            "subjectName": {
                                "title": "",
                                "firstName": credit_party.name,
                                "middleName": "",
                                "lastName": "",
                                "fullName": "",
                                "nativeName": ""
                            },
                            "emailAddress": "",
                            "birthCountry": ""
                        },
                        "recipientKyc": {
                            "nationality": "",
                            "dateOfBirth": "",
                            "occupation": "",
                            "employerName": "",
                            "contactPhone": "",
                            "gender": "",
                            "idDocument": [{
                                "idType": "",
                                "idNumber": "",
                                "issueDate": "",
                                "expiryDate": "",
                                "issuer": "",
                                "issuerPlace": "",
                                "issuerCountry": "",
                                "otherIdDescription": ""
                            }],
                            "postalAddress": {
                                "addressLine1": "",
                                "addressLine2": "",
                                "addressLine3": "",
                                "city": "",
                                "stateProvince": "",
                                "postalCode": "",
                                "country": ""
                            },
                            "subjectName": {
                                "title": "",
                                "firstName": debit_party.name,
                                "middleName": "",
                                "lastName": "",
                                "fullName": "",
                                "nativeName": ""
                            },
                            "emailAddress": "",
                            "birthCountry": ""
                        },
                        "originalTransactionReference": "",
                        "servicingIdentity": "",
                        "requestingLei": "",
                        "receivingLei": "",
                        "metadata": [{
                            "key": "",
                            "value": ""
                        }],
                        "transactionStatus": transaction.state,
                        "creationDate": transaction.created_at,
                        "modificationDate": transaction.modified_at,
                        "transactionReference": "",
                        "transactionReceipt": "",
                        "internationalTransferInformation": {
                            "originCountry": "",
                            "quotationReference": "",
                            "quoteId": "",
                            "receivingCountry": "",
                            "remittancePurpose": "1",
                            "relationshipSender": "",
                            "deliveryMethod": "",
                            "senderBlockingReason": "",
                            "recipientBlockingReason": ""
                        }
                    })

                # payload.append({
                #     'test': test
                # })
                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accounttransactionsbyaccount_id_200",
                            status=status.HTTP_200_OK,
                            key="wallet_id",
                            wallet_id=str(account_id)
                            )
                return response
            else:
                logger.info("get_accounttransactionsbyaccount_id_404",
                            status=status.HTTP_404_NOT_FOUND,
                            wallet_id=str(account_id),
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="wallet_id",
                    wallet_id=account_id,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_accounttransactionsbymsisdn_404",
                        status=status.HTTP_404_NOT_FOUND,
                        wallet_id=str(account_id),
                        key="wallet_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="wallet_id",
                value=account_id,
                status=status.HTTP_404_NOT_FOUND
            )


class GetStatementEntriesByMsisdn(APIView):
    """
    This API fetches the customers last five transactions given the msisdn
    HTTP Method: GET
    URI: /accounts/msisdn/{msisdn}/statemententries/
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

    def get(self, request, msisdn):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_statemententries_404",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=msisdn,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)
            account_status = account.status
            if account_status == CustomerWallet.active:
                transactions = account.get_account_transactions()
                payload = []
                for transaction in transactions:
                    debit_party_msisdn = CustomerWallet.objects.get(
                        wallet_id=transaction.destination.wallet_id).msisdn
                    credit_party_msisdn = CustomerWallet.objects.get(
                        wallet_id=transaction.source.wallet_id).msisdn

                    payload.append({
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
                            key="msisdn",
                            msisdn=msisdn
                            )
                return response
            else:
                logger.info("get_statemententries_404",
                            status=status.HTTP_404_NOT_FOUND,
                            msisdn=msisdn,
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="msisdn",
                    value=msisdn,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_stamententries_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND
            )


class GetStatementEntriesByAccountID(APIView):
    """
    This API fetches the customers last five transactions given the accountID
    HTTP Method: GET
    URI: /accounts/msisdn/{msisdn}/statemententries/
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

    def get(self, request, wallet_id):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_statemententries_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=str(wallet_id),
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=wallet_id,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(wallet_id=wallet_id)
            account_status = account.status
            if account_status == CustomerWallet.active:
                transactions = account.get_account_transactions()
                payload = []
                for transaction in transactions:
                    debit_party_msisdn = CustomerWallet.objects.get(
                        wallet_id=transaction.destination.wallet_id).msisdn
                    credit_party_msisdn = CustomerWallet.objects.get(
                        wallet_id=transaction.source.wallet_id).msisdn

                    payload.append({
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
                            key="wallet_id",
                            wallet_id=str(wallet_id)
                            )
                return response
            else:
                logger.info("get_statemententries_404",
                            status=status.HTTP_404_NOT_FOUND,
                            wallet_id=str(wallet_id),
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="wallet_id",
                    value=wallet_id,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_stamententries_404",
                        status=status.HTTP_404_NOT_FOUND,
                        wallet_id=str(wallet_id),
                        key="wallet_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="wallet_id",
                value=wallet_id,
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            logger.info("get_stamententries_400",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=str(wallet_id),
                        key="wallet_id"
                        )
            return send_error_response(
                message="Malformed UUID",
                key="wallet_id",
                value=wallet_id,
                status=status.HTTP_400_BAD_REQUEST)


class GetBillsByMsisdn(APIView):
    """
    This API fetches bills tied to a particular MSISDN
    HTTP Method: GET
    URI: /accounts/{accountid}/bills/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    [{
        "currency" : "",
        "amountDue" : "",
        "dueDate" : "",
        "billReference" : "",
        "minimumAmountDue" : "",
        "billDescription" : "",
        "metaData" : [ {
        "key" : "",
        "value" : ""
        } ]
    }]
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

    def get(self, request, msisdn):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_bills_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=msisdn,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)
            bills = account.get_account_bills()
            payload = []
            for bill in bills:
                biller_msisdn = CustomerWallet.objects.get(
                    wallet_id=bill.biller.wallet_id).msisdn
                payload.append({
                    "currency": bill.currency,
                    "amountDue": bill.amount_due,
                    "dueDate": bill.due_date,
                    "billReference": bill.bill_reference,
                    "minimumAmountDue": bill.bill_reference,
                    "billDescription": bill.bill_description,
                    "metaData":
                        [{
                            "key": "billerMsisdn",
                            "value": biller_msisdn
                        },
                            {
                                "key": "billStatus",
                                "value": bill.bill_status
                            }]
                })

            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_billss_200",
                        status=status.HTTP_200_OK,
                        key="msisdn",
                        msisdn=msisdn
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_bills_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND
            )


class GetBillsByAccountID(APIView):
    """
    This API fetches bills tied to a particular AccountID
    HTTP Method: GET
    URI: /accounts/msisdn/{msisdn}/bills/
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "currency" : "",
        "amountDue" : "",
        "dueDate" : "",
        "billReference" : "",
        "minimumAmountDue" : "",
        "billDescription" : "",
        "metaData" : [ {
        "key" : "",
        "value" : ""
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

    def get(self, request, wallet_id):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_bills_404",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=str(wallet_id),
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=wallet_id,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(wallet_id=wallet_id)
            bills = account.get_account_bills()
            payload = []
            for bill in bills:
                biller_msisdn = CustomerWallet.objects.get(
                    wallet_id=bill.biller.wallet_id).msisdn
                payload.append({
                    "currency": bill.currency,
                    "amountDue": bill.amount_due,
                    "dueDate": bill.due_date,
                    "billReference": bill.bill_reference,
                    "minimumAmountDue": bill.bill_reference,
                    "billDescription": bill.bill_description,
                    "metaData":
                        [{
                            "key": "billerMsisdn",
                            "value": biller_msisdn
                        }]
                })

            response = Response(data=payload,
                                status=status.HTTP_200_OK
                                )
            logger.info("get_bills_200",
                        status=status.HTTP_200_OK,
                        key="wallet_id",
                        wallet_id=str(wallet_id)
                        )
            return response

        except ObjectDoesNotExist:
            logger.info("get_bills_404",
                        status=status.HTTP_404_NOT_FOUND,
                        wallet_id=str(wallet_id),
                        key="wallet_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="wallet_id",
                value=wallet_id,
                status=status.HTTP_404_NOT_FOUND
            )

        except ValueError:
            logger.info("get_bills_404",
                        status=status.HTTP_404_NOT_FOUND,
                        wallet_id=str(wallet_id),
                        key="wallet_id"
                        )
            return send_error_response(
                message="Malformed UUID",
                key="wallet_id",
                value=wallet_id,
                status=status.HTTP_404_NOT_FOUND)


class GetDebitMandateByAccountId(APIView):
    """
    This API fetches the customers transactions given an msisdn
    HTTP Method: GET
    URI: /accounts/{accountId}/debitmandates/{debitMandateReference}
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "currency" : "",
        "amountLimit" : "",
        "startDate" : "",
        "endDate" : "",
        "numberOfPayments" : "",
         "frequencyType" : "",
         "mandateStatus" : "",
         "requestDate" : "",
         "mandateReference" : "",
         "creationDate" : "",
         "modificationDate" : ""
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

    def get(self, request, account_id, debit_mandate_reference):
        date = request.META.get("HTTP_DATE")

        if not date:
            logger.info("get_debitmandatebyaccount_id_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        wallet_id=account_id,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=account_id,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(wallet_id=account_id)

            debit_mandate = DebitMandate.objects \
                .all().filter(account=account). \
                get(mandate_reference=debit_mandate_reference)
            account_status = account.status

            if account_status == CustomerWallet.active:
                payload = {
                    "currency": debit_mandate.currency,
                    "amountLimit": debit_mandate.amount_limit,
                    "startDate": debit_mandate.start_date,
                    "endDate": debit_mandate.end_date,
                    "numberOfPayments": debit_mandate.number_of_payments,
                    "frequencyType": debit_mandate.frequency_type,
                    "mandateStatus": debit_mandate.mandate_status,
                    "requestDate": debit_mandate.request_date,
                    "mandateReference": debit_mandate.mandate_reference,
                    "creationDate": debit_mandate.created_at,
                    "modificationDate": debit_mandate.modified_at
                }

                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_debitmandatebyaccount_id_200",
                            status=status.HTTP_200_OK,
                            key="wallet_id",
                            wallet_id=str(account_id)
                            )
                return response
            else:
                logger.info("get_debitmandatebyaccount_id_404",
                            status=status.HTTP_404_NOT_FOUND,
                            wallet_id=str(account_id),
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="wallet_id",
                    wallet_id=account_id,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_debitmandatebyaccount_id_404",
                        status=status.HTTP_404_NOT_FOUND,
                        wallet_id=str(account_id),
                        key="wallet_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="wallet_id",
                value=account_id,
                status=status.HTTP_404_NOT_FOUND
            )


class GetDebitMandateByMsisdn(APIView):
    """
    This API fetches the customers transactions given an msisdn
    HTTP Method: GET
    URI: /accounts/{msisdn}/debitmandates/{debitMandateReference}
    Required HTTP Headers:
    DATE: todays date
    AUTHORIZATION: api-key
    CONTENT-TYPE: application/json
    Success response:
    HTTP status code: 200
    {
        "currency" : "",
        "amountLimit" : "",
        "startDate" : "",
        "endDate" : "",
        "numberOfPayments" : "",
         "frequencyType" : "",
         "mandateStatus" : "",
         "requestDate" : "",
         "mandateReference" : "",
         "creationDate" : "",
         "modificationDate" : ""
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

    def get(self, request, msisdn, debit_mandate_reference):
        date = request.META.get("HTTP_DATE")

        if not date:
            logger.info("get_debitmandatebymsisdn_400",
                        message="DATE Header not supplied",
                        status=status.HTTP_400_BAD_REQUEST,
                        msisdn=msisdn,
                        key="DATE"
                        )
            return send_error_response(
                message="DATE Header not supplied",
                key="DATE",
                value=msisdn,
                status=status.HTTP_400_BAD_REQUEST
            )

        # try to get the wallet id this msisdn maps to
        try:
            account = CustomerWallet.objects.get(msisdn=msisdn)

            debit_mandate = DebitMandate.objects \
                .all().filter(account=account). \
                get(mandate_reference=debit_mandate_reference)
            account_status = account.status

            if account_status == CustomerWallet.active:
                payload = {
                    "currency": debit_mandate.currency,
                    "amountLimit": debit_mandate.amount_limit,
                    "startDate": debit_mandate.start_date,
                    "endDate": debit_mandate.end_date,
                    "numberOfPayments": debit_mandate.number_of_payments,
                    "frequencyType": debit_mandate.frequency_type,
                    "mandateStatus": debit_mandate.mandate_status,
                    "requestDate": debit_mandate.request_date,
                    "mandateReference": debit_mandate.mandate_reference,
                    "creationDate": debit_mandate.created_at,
                    "modificationDate": debit_mandate.modified_at
                }

                response = Response(data=payload,
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_debitmandatebymsisdn_200",
                            status=status.HTTP_200_OK,
                            key="msisdn",
                            msisdn=msisdn
                            )
                return response
            else:
                logger.info("get_debitmandatebymsisdn_404",
                            status=status.HTTP_404_NOT_FOUND,
                            msisdn=msisdn,
                            key="account_inactive"
                            )
                return send_error_response(
                    message="Requested resource not active",
                    key="msisdn",
                    msisdn=msisdn,
                    status=status.HTTP_404_NOT_FOUND
                )

        except ObjectDoesNotExist:
            logger.info("get_debitmandatebymsisdn_404",
                        status=status.HTTP_404_NOT_FOUND,
                        msisdn=msisdn,
                        key="msisdn"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="msisdn",
                value=msisdn,
                status=status.HTTP_404_NOT_FOUND
            )


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.
    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}
    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.
    Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == str(uuid_obj)
