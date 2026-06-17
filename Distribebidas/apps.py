from django.apps import AppConfig

class DistribebidasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Distribebidas'

    def ready(self):
       from . import signals
