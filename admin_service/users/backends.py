import logging
import uuid
from typing import Any
from uuid import UUID

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from jose import JWTError, jwt

logger = logging.getLogger(__name__)

User = get_user_model()


class AdminBackend(BaseBackend):
    def authenticate(
        self,
        request: Any,
        username: str | None = None,
        password: str | None = None,
    ) -> User | None:
        """
        Аутентификация пользователя через auth_service.

        Отправляет POST-запрос на указанный URL аутентификации с переданными
        именем пользователя и паролем. При успешном ответе извлекает JWT-токен,
        декодирует его и на основании полученных данных создает или обновляет
        пользователя в локальной базе данных.
        """
        logger.info(
            'Начало аутентификации пользователя через auth_service. '
            'login=%s, password=%s',
            username, password
        )
        url = settings.AUTH_API_LOGIN_URL
        payload = {'username': username, 'password': password}
        headers = {
            'X-Source-Service': 'admin_service',
            'X-Request-Id': str(uuid.uuid4()),
        }
        try:
            response = requests.post(
                url, data=payload, headers=headers, timeout=5
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.error(
                'Ошибка запроса при аутентификации пользователя через '
                'auth_service: %s login=%s, password=%s',
                e, username, password
            )
            return None

        try:
            data = response.json()

        except requests.exceptions.JSONDecodeError as e:
            logger.error(
                'Ошибка декодирования JSON из ответа при аутентификации '
                'пользователя через auth_service: %s login=%s, password=%s',
                e, username, password
            )
            return None

        token = data.get('access_token')
        if not token:
            logger.error(
                'Ошибка при аутентификации пользователя через auth_service: '
                'В полученных данных нет access_token. login=%s, password=%s',
                username, password
            )
            return None

        try:
            decoded = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except JWTError as e:
            logger.error(
                'Ошибка декодирования токена при аутентификации пользователя '
                'через auth_service: %s login=%s, password=%s, token=%s',
                e, username, password, token
            )
            return None

        if (user_id := decoded.get('user_id')) and (
                role := decoded.get('role')
        ):
            try:
                user, created = User.objects.get_or_create(id=user_id,)
                user.login = username
                user.is_staff = True if role in (
                    'superuser', 'admin'
                ) else False
                user.is_superuser = True if role in ('superuser',) else False

                user.save()

            except (IntegrityError, DatabaseError, ValidationError) as e:
                logger.error(
                    'Ошибка получения или сохранения пользователя (ID: %s) '
                    'при аутентификации пользователя через auth_service: %s'
                    'login=%s, password=%s',
                    user_id, e, username, password
                )
                return None

            return user

        logger.error(
            'Ошибка при аутентификации пользователя через auth_service: '
            'В payload отсутствуют необходимые данные. '
            'login=%s, password=%s, decoded=%s',
            username, password, decoded
        )

    def get_user(self, user_id: UUID) -> User | None:
        """Получает объект пользователя по заданному идентификатору."""
        try:
            return User.objects.get(pk=user_id)

        except User.DoesNotExist:
            return None
