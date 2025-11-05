"""
Legacy scheduler jobs module.
Теперь используется Celery для всех фоновых задач.
Этот файл оставлен для обратной совместимости.
"""

from news.tasks import send_weekly_digest


def weekly_digest_job():
    """
    Раз в неделю отправляет подписчикам каждой категории список новых статей за 7 дней.
    
    ВНИМАНИЕ: Эта функция теперь просто вызывает Celery задачу.
    Для автоматического запуска используется Celery Beat (каждый понедельник в 8:00).
    Для ручного запуска используйте: news.tasks.send_weekly_digest.delay()
    """
    # Вызываем Celery задачу синхронно (для обратной совместимости)
    # В production используйте send_weekly_digest.delay() для асинхронного выполнения
    return send_weekly_digest()

