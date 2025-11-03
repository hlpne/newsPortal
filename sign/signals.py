from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site


@receiver(user_signed_up)
def send_welcome_with_activation(request, user, **kwargs):
    # Получаем primary EmailAddress (должен быть создан allauth)
    try:
        email_address = EmailAddress.objects.get(user=user, email=user.email)
    except EmailAddress.DoesNotExist:
        return

    # Генерим ключ и ссылку активации вида /accounts/confirm-email/<key>/
    confirm = EmailConfirmationHMAC(email_address)
    activation_path = reverse('account_confirm_email', args=[confirm.key])

    # Собираем абсолютный URL через Site
    try:
        current_site = Site.objects.get_current()
        protocol = 'https' if settings.DEBUG == False else 'http'
        activation_url = f"{protocol}://{current_site.domain}{activation_path}"
    except (Site.DoesNotExist, AttributeError):
        activation_url = f"http://localhost:8000{activation_path}"

    context = {
        'user': user,
        'activation_url': activation_url,
    }
    html = render_to_string('emails/welcome.html', context)
    text = f"""Привет, {user.get_username()}!
Добро пожаловать в News Portal.
Пожалуйста, активируйте аккаунт: {activation_url}
"""

    send_mail(
        subject='Добро пожаловать в News Portal!',
        message=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html,
        fail_silently=False,
    )

