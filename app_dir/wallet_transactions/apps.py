from django.apps import AppConfig


class WalletTransactionsConfig(AppConfig):
    """
    Wallet transaction app Config
    """
    name = 'app_dir.wallet_transactions'
    verbose_name = 'Wallet Transactions'
    app_label = 'wallet_transactions'

    def ready(self, ):
        pass