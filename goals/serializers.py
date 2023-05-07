from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания категории
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board: Board) -> Board:
        if board.is_deleted:
            raise serializers.ValidationError('Доска удалена')

        if not BoardParticipant.objects.filter(
                board_id=board.id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied

        return board

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериалайзер для категирии
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "user", "created", "updated")

    def validate_category(self, category):
        if category.is_deleted:
            raise ValidationError(message="Категория не найдена")

        if not BoardParticipant.objects.filter(
            board_id=category.board_id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied

        return category


class GoalSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для цели
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Goal
        read_only_fields = ('id', 'user', 'created', 'updated')
        fields = '__all__'


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания коммента цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created', 'updated')

    def validate_goal(self, value: Goal):
        if not BoardParticipant.objects.filter(
                board=value.category.board.id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ):
            raise PermissionDenied
        return value


class GoalCommentSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для комментария цели
    """
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'goal')


class BoardCreateSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для создания доски
    """
    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')


class BoardParticipantsSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для пользователей доской
    """
    role = serializers.ChoiceField(required=True, choices=BoardParticipant.Role.choices[1:])
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для доски
    """
    participants = BoardParticipantsSerializer(many=True)

    class Meta:
        model = Board
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')

    def update(self, instance: Board, validated_data: dict) -> Board:
        request: Request = self.context['request']
        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request.user).delete()
            BoardParticipant.objects.bulk_create(
                [
                    BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                    for participant in validated_data.get('participants', [])
                ],
                ignore_conflicts=True
            )

            if title := validated_data.get('title'):
                instance.title = title

            instance.save()

        return instance


class BoardListSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для отображения всех досок
    """
    class Meta:
        model = Board
        fields = '__all__'
