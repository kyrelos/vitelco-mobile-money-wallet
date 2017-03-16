from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from structlog import get_logger

from .models import CustomerWallet
from .serializers import CustomerWalletSerializer, \
    CustomerWalletStatusSerializer


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


class GetAccountName(APIView):
    """
    This API retrieves the customers name details given a msisdn
    HTTP Method: GET
    URI: /api/v1/accounts/msisdn/{msisdn}/accountname/

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
            return self.send_error_response(
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
                                    content_type="application/json",
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
                return self.send_error_response(
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

            return self.send_error_response(
                    message="Requested resource not available",
                    key="msisdn",
                    value=msisdn,
                    status=status.HTTP_404_NOT_FOUND
            )

    @staticmethod
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
