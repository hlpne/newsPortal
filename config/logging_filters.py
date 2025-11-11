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
        
        # Для ERROR и CRITICAL добавляем exc_info, если он есть
        if record.levelno >= logging.ERROR and record.exc_info:
            result += '\n' + self.formatException(record.exc_info)
        
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

