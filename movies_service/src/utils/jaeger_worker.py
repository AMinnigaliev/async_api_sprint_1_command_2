import asyncio
import functools

from opentelemetry import trace
from opentelemetry.trace import set_span_in_context

from src.core.config import settings
from src.core.jaeger_init import tracer


class JaegerWorker:
    """Клас-обработчик событий opentelemetry."""

    @staticmethod
    def set_span_attribute(key: str, value) -> None:
        """
        Установка атрибута в текущий span.

        @type key: str
        @param key:
        @type value:
        @param value:

        @rtype:
        @return:
        """
        span = trace.get_current_span()

        if span.get_span_context().is_valid:
            span.set_attribute(key=key, value=value)

    @staticmethod
    def start_span(span_name: str | None = None):
        """
        Декоратор, добавляющий выполнение метода/функции в отдельный span
        текущего context.

        @type span_name: str | None
        @param span_name:

        @rtype:
        @return:
        """
        def wrapper(func):

            @functools.wraps(func)
            async def async_wrapped(*args, **kwargs):
                if settings.enable_jaeger:
                    new_span_name = span_name if span_name else func.__name__
                    parent_span = trace.get_current_span()

                    if parent_span.get_span_context().is_valid:
                        span_context = set_span_in_context(parent_span)

                    else:
                        span_context = None

                    with tracer.start_as_current_span(
                            new_span_name, context=span_context
                    ):
                        return await func(*args, **kwargs)

                else:
                    return await func(*args, **kwargs)

            @functools.wraps(func)
            def sync_wrapped(*args, **kwargs):
                if settings.enable_jaeger:
                    new_span_name = span_name if span_name else func.__name__
                    parent_span = trace.get_current_span()

                    if parent_span.get_span_context().is_valid:
                        span_context = set_span_in_context(parent_span)

                    else:
                        span_context = None

                    with tracer.start_as_current_span(
                            new_span_name, context=span_context
                    ):
                        return func(*args, **kwargs)

                else:
                    return func(*args, **kwargs)

            if asyncio.iscoroutinefunction(func):
                return async_wrapped

            else:
                return sync_wrapped

        return wrapper
