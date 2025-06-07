import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeliveryMethod(models.Model):
    """
    Справочник способов доставки (email, sms, push).
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('Method code'),
        help_text=_('Уникальный код метода доставки, например "email".')
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_('Method name'),
        help_text=_('Читабельное имя, например "Email".')
    )

    class Meta:
        db_table = 'notify"."delivery_method'
        verbose_name = _('delivery method')
        verbose_name_plural = _('delivery methods')

    def __str__(self):
        return self.name


class OutgoingMessage(models.Model):
    """
    Хранит одно сообщение для отправки во внешний Notify_API.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('ID'),
        help_text=_('Unique UUID for tracking notifications in services'),
    )
    title = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Message title'),
        help_text=_('Title of the message'),
    )
    body = models.TextField(
        verbose_name=_('Message body'),
        help_text=_('Text of the message (HTML or plain text)'),
    )
    url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Message url'),
        help_text=_('Optional link that can be included in the message'),
    )
    user_ids = models.TextField(
        blank=True,
        verbose_name=_('User IDs'),
        help_text=_('UUIDs of users separated by commas, without spaces'),
    )
    to_all_users = models.BooleanField(
        default=False,
        verbose_name=_('Send to all users'),
        help_text=_('If enabled, the recipients field is ignored'),
    )
    delivery_methods = models.ManyToManyField(
        'DeliveryMethod',
        related_name='messages',
        verbose_name=_('Delivery methods'),
        help_text=_('Select one or more shipping methods.'),
    )
    execution_at = models.DateTimeField(
        verbose_name=_('Execution at (date/time)'),
        help_text=_('When the Notify_worker should process this message'),
    )
    success = models.BooleanField(
        default=False,
        verbose_name=_('Successfully sent to Notify_API'),
        help_text=_('True if the external service responded with 200 OK'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )

    class Meta:
        db_table = 'notify"."outgoing_message'
        verbose_name = _('message for mailing list')
        verbose_name_plural = _('messages for mailing list')
        ordering = ('-created_at',)

    def __str__(self):
        mark = '▶️' if not self.success else '✅'
        methods = ", ".join(m.code for m in self.delivery_methods.all())
        base = f'{mark} [{methods}] {self.title} (send_at={self.execution_at})'
        if self.url:
            base += f' | 🔗 {self.url}'
        return base

    def get_user_ids_list(self) -> list[str]:
        """Возвращает список строк-UUID получателей."""
        if self.to_all_users:
            return []

        user_ids = []
        for user_id in self.user_ids.split(','):
            user_id = user_id.strip()
            try:
                user_id = uuid.UUID(user_id)
                user_ids.append(str(user_id))

            except (ValueError, AttributeError):
                continue

        return user_ids
