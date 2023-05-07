from typing import Any

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from bot.models import TgUser
from bot.serializer import TgUserSerializer
from bot.tg.client import TgClient


class VerificationView(GenericAPIView):
    model = TgUser
    permission_classes = [IsAuthenticated]
    serializer_class = TgUserSerializer

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            tg_user = TgUser.objects.get(verification_code=serializer.validated_data['verification_code'])
        except TgUser.DoesNotExist:
            raise AuthenticationFailed

        tg_user.user = request.user
        tg_user.save()

        TgClient().send_message(tg_user.chat_id, 'verification has been completed')

        return Response(self.get_serializer(tg_user).data)
