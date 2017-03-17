from datetime import datetime
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from .models import CustomerWallet
from .serializers import CustomerWalletSerializer, CustomerWalletStatusSerializer

logger = get_logger("accounts")


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


class getAccountStatus(APIView):
    def get(self, request, msisdn):
        account = CustomerWallet.objects.get(msisdn=msisdn)
        if account is not None:
            serializer = CustomerWalletStatusSerializer(account)
            return Response(serializer.data)
        else:
            return Response(status.HTTP_404_NOT_FOUND)


class AccountBalanceByMsisdn(APIView):
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
                    'balance': account.get_available_balance()
                }
                response = Response(data=payload,
                                    content_type="application/json",
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
    def get(self, request, account_id):
        date = request.META.get("HTTP_DATE")
        if not date:
            logger.info("get_accountbalancebyaccountid_400",
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

        if not is_valid_uuid(account_id):
            logger.info("get_accountbalancebyaccountid_400",
                        message="account_id invalid",
                        status=status.HTTP_400_BAD_REQUEST,
                        account_id=account_id,
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
                    'balance': account.get_available_balance()
                }
                response = Response(data=payload,
                                    content_type="application/json",
                                    status=status.HTTP_200_OK
                                    )
                logger.info("get_accountbalancebyaccountid_200",
                            status=status.HTTP_200_OK,
                            key="account_id",
                            account_id=account_id
                            )
                return response
            else:
                logger.info("get_accountbalancebyaccountid_404",
                            status=status.HTTP_404_NOT_FOUND,
                            account_id=account_id,
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
                        account_id=account_id,
                        key="account_id"
                        )

            return send_error_response(
                message="Requested resource not available",
                key="account_id",
                value=account_id,
                status=status.HTTP_404_NOT_FOUND
            )


def send_error_response(message="404",
                        key="msisdn",
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
    except:
        return False

    return str(uuid_obj) == uuid_to_test
