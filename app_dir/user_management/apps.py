from django.apps import AppConfig


class UserManagementConfig(AppConfig):
    """
    """
    name = 'app_dir.user_management'
    verbose_name = 'User Management'
    app_label = 'user_management'

    def ready(self, ):
        pass