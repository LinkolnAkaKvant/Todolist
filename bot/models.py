import os

from django.db import models

from core.models import User


class TgUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    verification_code = models.CharField(max_length=50, null=True, blank=True, default=None)

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'

    @staticmethod
    def _generate_verification_code():
        return os.urandom(12).hex()

    def set_verification_code(self):
        code = self._generate_verification_code()
        self.verification_code = code
        self.save(update_fields=('verification_code',))

        return code
