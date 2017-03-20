from django.apps import AppConfig


class DebitMandateManagementConfig(AppConfig):
    """
    Debit mandate manager app Config
    """
    name = 'app_dir.debit_mandate_management'
    verbose_name = 'Debit Mandate Management'
    app_label = 'debit_mandate_management'

    def ready(self, ):
        pass