"""
Management command для запуска APScheduler с еженедельным дайджестом.
Использование: python manage.py runapscheduler
"""
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from scheduler.jobs import weekly_digest_job

logger = logging.getLogger(__name__)


def delete_old_job_executions(max_age=604_800):
    """Удаляет старые записи выполнения задач APScheduler (старше max_age секунд)"""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Запускает APScheduler с еженедельным дайджестом"

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Еженедельный дайджест - каждый понедельник в 09:00
        scheduler.add_job(
            weekly_digest_job,
            trigger=CronTrigger(day_of_week="mon", hour="09", minute="00"),
            id="weekly_digest",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'weekly_digest' (каждый понедельник в 09:00)")

        # Очистка старых записей - каждый понедельник в 00:00
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'delete_old_job_executions' (каждый понедельник в 00:00)")

        try:
            logger.info("Запуск планировщика...")
            self.stdout.write(self.style.SUCCESS('Планировщик запущен. Нажмите Ctrl+C для остановки.'))
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен!")
            self.stdout.write(self.style.SUCCESS('Планировщик остановлен.'))

