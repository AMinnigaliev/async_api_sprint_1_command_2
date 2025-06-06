import logging
import uuid
from datetime import UTC, datetime, timedelta

import requests
from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .forms import OutgoingMessageForm
from .models import DeliveryMethod, OutgoingMessage

logger = logging.getLogger(__name__)


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OutgoingMessage)
class OutgoingMessageAdmin(admin.ModelAdmin):
    """Админ-интерфейс для модели OutgoingMessage."""
    form = OutgoingMessageForm

    list_display = (
        'title', 'send_summary', 'to_all_users', 'success', 'created_at'
    )
    list_filter = ('delivery_methods', 'to_all_users', 'success', 'created_at')
    search_fields = ('title', 'body', 'user_ids')
    readonly_fields = ('success', 'created_at')
    list_display_links = None

    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'delivery_methods')
        }),
        ('Получатели', {
            'fields': ('to_all_users', 'user_ids'),
            'description': (
                'Если отмечен флажок «Отправить всем», то все пользователи. '
                'Иначе — перечислите UUID получателей через запятую.'
            )
        }),
        ('Время отправки', {
            'fields': ('execution_at',),
            'description': (
                'Дата и время (UTC), когда воркер обработает сообщение.'
            )
        }),
        ('Статус', {
            'fields': ('success', 'created_at',)
        }),
    )

    def send_summary(self, obj):
        """Отображает компактно все коды способов доставки."""
        return ", ".join([m.code for m in obj.delivery_methods.all()])

    send_summary.short_description = _('Delivery Methods')

    def save_model(self, request, obj, form, change):
        """
        При сохранении (и создании, и обновлении) отправляем синхронный
        HTTP-запрос в Notify_API. Если Notify_API вернул 2xx → success=True,
        иначе → False.
        """
        request_id = str(uuid.uuid4())
        user_ids = obj.get_user_ids_list()
        relevance_at = obj.execution_at + timedelta(minutes=30)

        now = datetime.now(UTC)
        if obj.execution_at < now:
            obj.execution_at = now

        payload = {
            'id': obj.id,
            'kwargs': {
                'meta': {
                    'send_at': datetime.now(UTC).isoformat(),
                    'X-Request-Id': request_id,
                    'execution_at': obj.execution_at.isoformat(),
                    'relevance_at': relevance_at.isoformat(),
                },
                'delivery_methods': obj.get_delivery_methods_list(),
                'notification_type': 'admin_info_message',
                'notification_data': {
                    'user_ids': user_ids,
                    'to_all_users': obj.to_all_users,
                    'data': {
                        'title': obj.title,
                        'body': obj.body,
                    },
                },
            },
        }

        url = settings.NOTIFY_API_URL

        try:
            headers = {
                'Content-Type': 'application/json',
                'X-Request-ID': request_id,
            }
            response = requests.post(
                url, json=payload, headers=headers, timeout=5
            )
            response.raise_for_status()
            obj.success = True

        except Exception as e:
            obj.success = False
            logger.error(
                '[OutgoingMessageAdmin] Ошибка при отправке в %s: %s',
                url, e
            )

        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return False
