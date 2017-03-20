from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from structlog import get_logger

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
                    "get_batch_transaction",
                    request=request,
                    kwargs={
                        "batch_trid":
                            "753bcd19-7230-40ba-a975-09ac94ace0d2"
                    }

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


