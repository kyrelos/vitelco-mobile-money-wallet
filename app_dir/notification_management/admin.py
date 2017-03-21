from django.contrib import admin
from .models import Notification, NotificationDeviceMap

admin.site.register(Notification)
admin.site.register(NotificationDeviceMap)