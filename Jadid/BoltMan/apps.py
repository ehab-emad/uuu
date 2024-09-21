from django.apps import AppConfig


class BoltManConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'BoltMan'
    verbose_name = 'Boltman'

class DashboardConfig(AppConfig):
    name = 'dashboard'
    default = False