from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from .models import Post


@receiver(post_save, sender=Post)
def notify_subscribers_on_create(sender, instance: Post, created, **kwargs):
    if not created:
        return

    # Получаем все категории поста
    categories = instance.categories.all()
    if not categories:
        return

    # Отправляем уведомления для каждой категории
    for category in categories:
        subscribers = category.subscribers.select_related().all()
        if not subscribers:
            continue

        # Персонально каждому: чтобы вставить username и корректно собрать ссылку
        for user in subscribers:
            subject = instance.title
            context = {
                'post': instance,
                'snippet': instance.text[:50],
                'user': user,
                'request': None,  # В сигнале нет request, используем настройки
            }
            
            # Создаем абсолютный URL (используем метод модели)
            relative_url = instance.get_absolute_url()
            try:
                current_site = Site.objects.get_current()
                protocol = 'https' if settings.DEBUG == False else 'http'
                abs_post_url = f"{protocol}://{current_site.domain}{relative_url}"
            except (Site.DoesNotExist, AttributeError):
                # Fallback если Site не настроен
                abs_post_url = f"http://localhost:8000{relative_url}"
            context['abs_post_url'] = abs_post_url
            
            html = render_to_string('emails/new_post_personal.html', context)
            text = f"""{instance.title}
{instance.text[:50]}…

Здравствуй, {user.get_username()}. Новая статья в твоём любимом разделе!

Читать на сайте: {context['abs_post_url']}
"""
            
            send_mail(
                subject=subject,
                message=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html,
                fail_silently=False,
            )
