"""Обработка ошибок, подтверждение действий, замеры времени и кэширование"""

import time

from primitive_db.constants import (
    CANCELLED_MESSAGE,
    CONFIRM_ANSWER,
    CONFIRM_PROMPT,
    FILE_ERROR_MESSAGE,
    FILE_NOT_FOUND_MESSAGE,
    KEY_ERROR_MESSAGE,
    KNOWN_ERROR_PREFIXES,
    TIME_MESSAGE,
    UNEXPECTED_ERROR_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
)


def preserve_metadata(wrapper, function):
    """Сохранить имя и описание функции"""
    wrapper.__name__ = function.__name__
    wrapper.__doc__ = function.__doc__
    wrapper.__module__ = function.__module__
    wrapper.__wrapped__ = function
    return wrapper


def handle_db_errors(func):
    """Вывести понятную ошибку операции; при неудаче вернуть None"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(FILE_NOT_FOUND_MESSAGE)
        except KeyError as error:
            print(KEY_ERROR_MESSAGE.format(error=error))
        except ValueError as error:
            message = str(error)
            if message.startswith(KNOWN_ERROR_PREFIXES):
                print(message)
            else:
                print(VALIDATION_ERROR_MESSAGE.format(error=error))
        except OSError as error:
            print(FILE_ERROR_MESSAGE.format(error=error))
        except Exception as error:
            print(UNEXPECTED_ERROR_MESSAGE.format(error=error))
        return None

    return preserve_metadata(wrapper, func)


def confirm_action(action_name):
    """Запросить подтверждение; любой ответ, кроме точного y, отменяет вызов."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                answer = input(CONFIRM_PROMPT.format(action_name=action_name))
            except (EOFError, KeyboardInterrupt):
                print()
                answer = ""
            if answer != CONFIRM_ANSWER:
                print(CANCELLED_MESSAGE)
                return None
            return func(*args, **kwargs)

        return preserve_metadata(wrapper, func)

    return decorator


def log_time(func):
    """Измерить продолжительность вызова монотонными часами"""
    def wrapper(*args, **kwargs):
        started = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started
            print(TIME_MESSAGE.format(function_name=func.__name__, elapsed=elapsed))

    return preserve_metadata(wrapper, func)


def create_cacher():
    """Вернуть функцию с независимым кэшем в замыкании и методом clear()"""
    cache = {}

    def cache_result(key, value_func):
        """Получить сохранённый результат либо вычислить его один раз"""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    def clear():
        """Очистить результаты после изменения данных"""
        cache.clear()

    cache_result.clear = clear
    return cache_result
