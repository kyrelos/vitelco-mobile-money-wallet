from django.apps import AppConfig


class WalletConfig(AppConfig):
    """
    """
    name = 'app_dir.wallet'
    verbose_name = 'Vitelco Wallet'
    app_label = 'wallet'

    def ready(self, ):
        pass