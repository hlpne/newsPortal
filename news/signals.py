from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from .tasks import notify_subscribers


@receiver(post_save, sender=Post)
def notify_subscribers_on_create(sender, instance: Post, created, **kwargs):
    """
    Сигнал для отправки уведомлений подписчикам через Celery при создании нового поста.
    """
    if not created:
        return

    # Получаем все категории поста
    categories = instance.categories.all()
    if not categories:
        return

    # Отправляем задачу в очередь Celery
    notify_subscribers.delay(instance.pk)
