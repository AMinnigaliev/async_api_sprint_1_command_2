from django.contrib.auth.base_user import BaseUserManager


class AdminUserManager(BaseUserManager):
    def create_user(self, login: str, password: str | None = None):
        """Создает и сохраняет пользователя с заданным логином и паролем."""
        if not login:
            raise ValueError('Users must have a login')

        user = self.model(login=login)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, login: str, password: str | None = None
    ):
        """
        Создает и сохраняет суперпользователя с заданным логином и паролем.
        """
        user = self.create_user(login, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user
