from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Модель пользователя
    """
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
