from rest_framework import serializers

from bot.models import TgUser


class TgUserSerializer(serializers.ModelSerializer):
    tg_id = serializers.ImageField(source='chat_id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = TgUser
        read_only_fields = ("tg_id", "username", "user_id")
        fields = ("tg_id", "username", "verification_code", "user_id")
