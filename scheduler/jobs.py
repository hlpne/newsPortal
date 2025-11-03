from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site
from news.models import Category, Post


def build_abs_url(path: str) -> str:
    """Строит абсолютный URL используя Site framework"""
    try:
        domain = Site.objects.get_current().domain
        scheme = 'https' if settings.DEBUG == False else 'http'
        return f'{scheme}://{domain}{path}'
    except (Site.DoesNotExist, AttributeError):
        return f'http://localhost:8000{path}'


def weekly_digest_job():
    """
    Раз в неделю отправляет подписчикам каждой категории список новых статей за 7 дней.
    Письмо содержит заголовки и кликабельные ссылки.
    """
    since = timezone.now() - timedelta(days=7)
    categories = Category.objects.prefetch_related('subscribers').all()

    for cat in categories:
        posts = Post.objects.filter(categories=cat, created_at__gte=since).order_by('-created_at')
        if not posts.exists():
            continue

        for user in cat.subscribers.all():
            subject = f'Еженедельный дайджест: {cat.name}'
            
            # Текстовая версия
            text_lines = [f'Привет, {user.get_username()}! Еженедельный дайджест категории "{cat.name}":\n']
            for p in posts:
                url = build_abs_url(p.get_absolute_url())
                text_lines.append(f'- {p.title} ({url})')
            text = '\n'.join(text_lines)
            
            # HTML версия
            html_items = []
            for p in posts:
                url = build_abs_url(p.get_absolute_url())
                html_items.append(f'<li><a href="{url}">{p.title}</a></li>')
            
            html = f"""
            <h3>Привет, {user.get_username()}!</h3>
            <p>Еженедельный дайджест категории «{cat.name}»:</p>
            <ul>{''.join(html_items)}</ul>
            """
            
            # Используем render_to_string для более красивого HTML
            context = {
                'user': user,
                'category': cat,
                'posts': posts,
            }
            # Обновляем контекст с правильными URL
            for p in context['posts']:
                p.abs_url = build_abs_url(p.get_absolute_url())
            
            html = render_to_string('emails/weekly_digest.html', context)

            send_mail(
                subject=subject,
                message=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html,
                fail_silently=False,
            )

