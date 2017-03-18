from django.apps import AppConfig


class BillManagementConfig(AppConfig):
    """
    Bill manager app Config
    """
    name = 'app_dir.bill_management'
    verbose_name = 'Bill Management'
    app_label = 'bill_management'

    def ready(self, ):
        pass