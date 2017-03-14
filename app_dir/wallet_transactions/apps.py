from django.apps import AppConfig


class WalletTransactionsConfig(AppConfig):
    """
    """
    name = 'app_dir.wallet_transactions'
    verbose_name = 'Vitelco Wallet Transactions'
    app_label = 'wallet_transactions'

    def ready(self, ):
        pass