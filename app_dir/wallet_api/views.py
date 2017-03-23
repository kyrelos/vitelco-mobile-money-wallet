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
                ),
                "Get transactions by msisdn": reverse(
                        "account:get_account_transactions_by_msisdn",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"msisdn": "+254711111111"}
                ),
                "Get transactions by accountId": reverse(
                        "account:get_account_transactions_by_account_id",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"account_id":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),

            },
            "BatchTransactions": {
                "Create batch transactions": reverse(
                        "batchtransactions", request=request
                ),
                "Get batch transaction by transaction reference": reverse(
                    "get_batch_transaction",
                    request=request,
                    kwargs={
                        "batch_trid":
                            "753bcd19-7230-40ba-a975-09ac94ace0d2"
                    }

                ),
                "Get batch completions": reverse(
                        "get_batch_transaction_by_state",
                        request=request,
                        kwargs={
                            "batch_trid":
                                "753bcd19-7230-40ba-a975-09ac94ace0d2",
                            "state": "completion"
                        }

                ),
                "Get batch rejections by transaction reference": reverse(
                        "get_batch_transaction_by_state",
                        request=request,
                        kwargs={
                            "batch_trid":
                                "753bcd19-7230-40ba-a975-09ac94ace0d2",
                            "state": "rejection"
                        }

                )
            },
            "Account": {
                "Get Account status by msisdn": reverse(
                    "account:get_account_status_by_msisdn",
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
                    kwargs={"msisdn": "+254711111111"}
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
                    kwargs={"msisdn": "+254711111111"}
                ),
                "Get Account balance by accountId": reverse(
                    "account:get_account_balance_by_account_id",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"account_id":
                                "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),

                "Get Account statement entries by msisdn": reverse(
                        "account:get_statement_by_msisdn",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"msisdn": "+254711111111"}
                ),
                "Get Account statement entries by accountId": reverse(
                        "account:get_statement_by_account_id",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"wallet_id":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),
                "Get specific statement by transaction reference": reverse(
                    "get_statement_by_trid",
                    request=request,
                    kwargs={"trid":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                )


            },
            "Debit Mandates": {
                "Create Debit Mandates with msisdn": reverse(
                    "account:debit_mandate_by_msisdn",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"msisdn":
                                "+254711111111"}
                ),

                "Create Debit Mandates with account Id": reverse(
                    "account:debit_mandate_by_account_id",
                    request=request,
                    current_app="customer_wallet_management",
                    kwargs={"account_id":
                                "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),
                "View a Debit Mandate by msisdn": reverse(
                        "account:get_debit_mandate_by_msisdn",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"msisdn":
                                    "+254711111111",
                                "debit_mandate_reference":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d3"
                                }
                ),
                "View a Debit Mandate by account id": reverse(
                        "account:get_debit_mandate_by_account_id",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"account_id":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d2",
                                "debit_mandate_reference":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d3"
                                }
                )

            },

            "Bills": {
                "Create Bills": reverse(
                        "create_bill",
                        request=request,
                ),
                "Get bills by msisdn": reverse(
                        "account:get_bills_by_msisdn",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"msisdn":
                                    "+254711111111"}
                ),

                "Get bills by account_id": reverse(
                        "account:get_bills_by_account_id",
                        request=request,
                        current_app="customer_wallet_management",
                        kwargs={"wallet_id":
                                    "753bcd19-7230-40ba-a975-09ac94ace0d2"}
                ),

            }
        }
        return Response(api_registry)


