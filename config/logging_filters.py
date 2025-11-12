"""
Custom logging filters and formatters for Django logging configuration.
"""
import logging
from django.conf import settings


class RequireDebugTrue(logging.Filter):
    """
    Filter that only allows log records when DEBUG = True.
    """
    def filter(self, record):
        return settings.DEBUG


class RequireDebugFalse(logging.Filter):
    """
    Filter that only allows log records when DEBUG = False.
    """
    def filter(self, record):
        return not settings.DEBUG


class ConsoleFormatter(logging.Formatter):
    """
    Custom formatter for console output that changes format based on log level:
    - DEBUG: time, level, message
    - WARNING and above: time, level, pathname, message
    - ERROR and CRITICAL: time, level, pathname, message, exc_info
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._base_fmt = '{asctime} {levelname} {message}'
        self._warning_fmt = '{asctime} {levelname} {pathname} {message}'
        self._error_fmt = '{asctime} {levelname} {pathname} {message}'
    
    def format(self, record):
        # Сохраняем оригинальный формат
        original_fmt = self._style._fmt
        
        # Выбираем формат в зависимости от уровня
        if record.levelno < logging.WARNING:
            self._style._fmt = self._base_fmt
        elif record.levelno < logging.ERROR:
            self._style._fmt = self._warning_fmt
        else:
            self._style._fmt = self._error_fmt
        
        # Форматируем запись
        result = super().format(record)
        
        # Восстанавливаем оригинальный формат
        self._style._fmt = original_fmt
        
        # Для ERROR и CRITICAL добавляем exc_info (стэк ошибки)
        if record.levelno >= logging.ERROR:
            if record.exc_info:
                result += '\n' + self.formatException(record.exc_info)
            elif record.exc_text:
                result += '\n' + record.exc_text
        
        return result


class ErrorsFormatter(logging.Formatter):
    """
    Custom formatter for errors.log that includes time, level, message, pathname, and exc_info.
    """
    def format(self, record):
        # Базовый формат: время, уровень, сообщение, pathname
        result = super().format(record)
        
        # Добавляем exc_info, если он есть
        if record.exc_info:
            result += '\n' + self.formatException(record.exc_info)
        
        return result


class AdminEmailHandler(logging.Handler):
    """
    Custom AdminEmailHandler that always uses SMTP, even when DEBUG=True.
    """
    def __init__(self, include_html=False, email_backend=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.include_html = include_html
        self.email_backend = email_backend or 'django.core.mail.backends.smtp.EmailBackend'
    
    def emit(self, record):
        from django.core.mail import get_connection
        from django.utils.log import AdminEmailHandler as DjangoAdminEmailHandler
        from django.conf import settings
        from pathlib import Path
        
        try:
            # Загружаем учетные данные из файла
            def load_email_credentials():
                credentials = {}
                credentials_file = Path(settings.BASE_DIR) / 'email_credentials.txt'
                if credentials_file.exists():
                    try:
                        with open(credentials_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#') and '=' in line:
                                    key, value = line.split('=', 1)
                                    key = key.strip()
                                    value = value.strip()
                                    if key == 'EMAIL_HOST_USER':
                                        credentials['EMAIL_HOST_USER'] = value
                                    elif key == 'EMAIL_HOST_PASSWORD':
                                        credentials['EMAIL_HOST_PASSWORD'] = value
                    except Exception:
                        pass
                return credentials
            
            email_credentials = load_email_credentials()
            
            # Создаем SMTP connection
            connection = get_connection(
                backend=self.email_backend,
                host=getattr(settings, 'EMAIL_HOST', 'smtp.mail.ru'),
                port=getattr(settings, 'EMAIL_PORT', 587),
                username=email_credentials.get('EMAIL_HOST_USER', getattr(settings, 'EMAIL_HOST_USER', '')),
                password=email_credentials.get('EMAIL_HOST_PASSWORD', getattr(settings, 'EMAIL_HOST_PASSWORD', '')),
                use_tls=getattr(settings, 'EMAIL_USE_TLS', True),
            )
            
            # Используем стандартный AdminEmailHandler с нашим SMTP connection
            handler = DjangoAdminEmailHandler(include_html=self.include_html)
            handler.connection = connection
            handler.emit(record)
        except Exception:
            self.handleError(record)

