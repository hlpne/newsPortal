"""
Celery tasks for News Portal.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from .models import Post, Category
from datetime import timedelta
from django.utils import timezone


def build_abs_url(path: str) -> str:
    """Строит абсолютный URL используя Site framework"""
    try:
        domain = Site.objects.get_current().domain
        scheme = 'https' if settings.DEBUG == False else 'http'
        return f'{scheme}://{domain}{path}'
    except (Site.DoesNotExist, AttributeError):
        return f'http://localhost:8000{path}'


@shared_task
def notify_subscribers(post_id):
    """
    Отправляет уведомления подписчикам категорий при создании новой новости/статьи.
    
    Args:
        post_id: ID поста, для которого нужно отправить уведомления
    """
    try:
        post = Post.objects.prefetch_related('categories__subscribers').get(pk=post_id)
    except Post.DoesNotExist:
        return f"Post with id {post_id} does not exist"
    
    # Получаем все категории поста
    categories = post.categories.all()
    if not categories:
        return f"No categories found for post {post_id}"
    
    emails_sent = 0
    
    # Отправляем уведомления для каждой категории
    for category in categories:
        subscribers = category.subscribers.select_related().all()
        if not subscribers:
            continue
        
        # Персонально каждому: чтобы вставить username и корректно собрать ссылку
        for user in subscribers:
            if not user.email:
                continue
                
            subject = post.title
            context = {
                'post': post,
                'snippet': post.text[:50],
                'user': user,
            }
            
            # Создаем абсолютный URL (используем метод модели)
            relative_url = post.get_absolute_url()
            context['abs_post_url'] = build_abs_url(relative_url)
            
            html = render_to_string('emails/new_post_personal.html', context)
            text = f"""{post.title}
{post.text[:50]}…

Здравствуй, {user.get_username()}. Новая статья в твоём любимом разделе!

Читать на сайте: {context['abs_post_url']}
"""
            
            try:
                send_mail(
                    subject=subject,
                    message=text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html,
                    fail_silently=False,
                )
                emails_sent += 1
            except Exception as e:
                # Логируем ошибку, но продолжаем отправку другим пользователям
                print(f"Error sending email to {user.email}: {e}")
    
    return f"Sent {emails_sent} notification emails for post {post_id}"


@shared_task
def send_weekly_digest():
    """
    Раз в неделю отправляет подписчикам каждой категории список новых статей за 7 дней.
    Письмо содержит заголовки и кликабельные ссылки.
    """
    since = timezone.now() - timedelta(days=7)
    categories = Category.objects.prefetch_related('subscribers').all()
    
    total_emails = 0
    
    for cat in categories:
        posts = Post.objects.filter(categories=cat, created_at__gte=since).order_by('-created_at')
        if not posts.exists():
            continue
        
        for user in cat.subscribers.all():
            if not user.email:
                continue
                
            subject = f'Еженедельный дайджест: {cat.name}'
            
            # Текстовая версия
            text_lines = [f'Привет, {user.get_username()}! Еженедельный дайджест категории "{cat.name}":\n']
            for p in posts:
                url = build_abs_url(p.get_absolute_url())
                text_lines.append(f'- {p.title} ({url})')
            text = '\n'.join(text_lines)
            
            # HTML версия
            context = {
                'user': user,
                'category': cat,
                'posts': posts,
            }
            # Обновляем контекст с правильными URL
            for p in context['posts']:
                p.abs_url = build_abs_url(p.get_absolute_url())
            
            html = render_to_string('emails/weekly_digest.html', context)
            
            try:
                send_mail(
                    subject=subject,
                    message=text,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html,
                    fail_silently=False,
                )
                total_emails += 1
            except Exception as e:
                print(f"Error sending weekly digest to {user.email}: {e}")
    
    return f"Sent {total_emails} weekly digest emails"

