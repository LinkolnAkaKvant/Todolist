from typing import Any

from rest_framework import permissions
from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import TgUser
from bot.serializer import TgUserSerializer

from bot.tg.client import TgClient
from todolist import settings


class VerificationView(GenericAPIView):
    model = TgUser
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tg_user = TgUser.objects.get(verification_code=serializer.validated_data["verification_code"])
        except TgUser.DoesNotExist:
            raise NotFound('Invalid verification code')
        else:
            tg_user.user = request.user
            tg_user.save()
            TgClient(settings.BOT_TOKEN).send_message(tg_user.chat_id, "Bot verification has been completed")

        return Response(TgUserSerializer(tg_user).data)
