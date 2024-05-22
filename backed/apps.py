from django.apps import AppConfig


class BackedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backed'




class BackedConfig(AppConfig):
    name = 'backed'

    def ready(self):
        import backed.signals
    