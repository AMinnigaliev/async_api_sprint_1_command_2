import uuid
from datetime import datetime, timedelta, timezone

from django.forms import ModelForm, ValidationError

from .models import OutgoingMessage


class OutgoingMessageForm(ModelForm):
    """
    Форма для создания и валидации исходящих сообщений.

    Проверяет:
    - наличие хотя бы одного способа доставки;
    - что поле execution_at не позже чем через неделю;
    - что указаны корректные UUID получателей, если не выбрано
    "Отправить всем";
    - что используется HTTPS.
    """

    class Meta:
        model = OutgoingMessage
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        methods = cleaned_data.get('delivery_methods')
        if not methods or methods.count() == 0:
            raise ValidationError({
                'delivery_methods':
                    'Нужно выбрать хотя бы один способ доставки.'
            })

    def clean_url(self) -> str:
        """Если не HTTPS кидаем ValidationError."""
        url = self.cleaned_data.get('url')
        if url and not url.startswith('https://'):
            raise ValidationError('Разрешены только URL-адреса HTTPS.')

        return url

    def clean_execution_at(self) -> str:
        """
        Если время выполнения отправки сообщения указано больше через неделю
        кидаем ValidationError.
        """
        execution_at = self.cleaned_data.get('execution_at')
        max_allowed_time = datetime.now(timezone.utc) + timedelta(weeks=1)
        if execution_at > max_allowed_time:
            raise ValidationError(
                'Время отправки не может быть больше, чем на 1 неделю вперед.'
            )

        return execution_at

    def clean_user_ids(self) -> str:
        """
        Если to_all_users=False, убеждаемся, что user ввёл хотя бы один
        корректный UUID, иначе кидаем ValidationError.
        """
        if self.cleaned_data.get('to_all_users'):
            return ''

        user_ids = self.cleaned_data.get('user_ids', '').strip()
        if not user_ids:

            raise ValidationError(
                'Если не отмечена галочка "Отправить всем", необходимо '
                'указать хотя бы один UUID.'
            )

        valid_user_ids = []
        for user_id in user_ids.split(','):
            user_id = user_id.strip()
            try:
                uid = uuid.UUID(user_id)
                valid_user_ids.append(str(uid))

            except (ValueError, AttributeError):
                raise ValidationError(
                    f'Неверный UUID: "{user_id}". Проверьте формат.'
                )

        return ",".join(valid_user_ids)
