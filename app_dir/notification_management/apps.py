from django.apps import AppConfig


class NotificationManagementConfig(AppConfig):
    """
    """
    name = 'app_dir.notification_management'
    verbose_name = 'Notification Management'
    app_label = 'notification_management'

    def ready(self, ):
        pass