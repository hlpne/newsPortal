from django.apps import AppConfig


class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    # Убираем автозапуск планировщика - теперь он запускается через management command
    # def ready(self):
    #     import os
    #     if os.environ.get('RUN_MAIN') == 'true':
    #         from . import scheduler  # noqa