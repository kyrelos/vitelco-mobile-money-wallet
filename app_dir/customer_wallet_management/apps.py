from django.apps import AppConfig


class CustomerWalletManagementConfig(AppConfig):
    """
    Customer wallet app Config
    """
    name = 'app_dir.customer_wallet_management'
    verbose_name = 'Customer Wallet Management'
    app_label = 'customer_wallet_management'

    def ready(self, ):
        pass