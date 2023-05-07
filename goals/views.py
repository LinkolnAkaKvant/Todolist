from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filter import GoalDateFilter, CategoryBoardFilter
from goals.models import GoalCategory, Goal, GoalComment, BoardParticipant, Board
from goals.permissions import BoardPermissions, GoalCategoryPermission, GoalPermission, CommentPermission
from goals.serializers import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardListSerializer, \
    BoardSerializer


class GoalCategoryCreateView(CreateAPIView):
    """Вью для создания категории"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    """Вью для показа всех категорий"""
    permission_classes = [GoalCategoryPermission]
    serializer_class = GoalCategorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CategoryBoardFilter
    ordering_fields = ('title', 'created')
    ordering = ['title']
    search_fields = ['title']

    def get_queryset(self):
        return GoalCategory.objects.prefetch_related('board__participants').filter(
            is_deleted=False, board__participants__user_id=self.request.user.id,
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    """
    Вью для изменения и удаления категорий
    """
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermission]

    def get_queryset(self):
        return GoalCategory.objects.select_related('user').filter(
            is_deleted=False, board__participants__user_id=self.request.user.id,
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.is_deleted = True
            instance.save(update_fields=('is_deleted',))
            instance.goals.update(status=Goal.Status.archived)


class GoalCreateView(CreateAPIView):
    """
    Вью для создания цели
    """
    permission_classes = [GoalPermission]
    serializer_class = GoalCreateSerializer


class GoalView(RetrieveUpdateDestroyAPIView):
    """
    Вью для работы с целью
    """
    permission_classes = [GoalPermission]
    serializer_class = GoalSerializer

    def get_queryset(self):
        return Goal.objects.select_related('category').filter(
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False) &
            Q(category__board__participants__user_id=self.request.user.id)
        )

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.status = Goal.Status.archived
            instance.save()


class GoalListView(ListAPIView):
    """
    Вью для отображения всех целей
    """
    permission_classes = [GoalPermission]
    serializer_class = GoalSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalDateFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created']
    ordering = ['title']

    def get_queryset(self):
        return Goal.objects.select_related('category').filter(
            ~Q(status=Goal.Status.archived) &
            Q(category__is_deleted=False) &
            Q(category__board__participants__user_id=self.request.user.id)
        )


class GoalCommentCreateView(CreateAPIView):
    """
    Вью для создания комментариев
    """
    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [GoalPermission]


class GoalCommentListView(ListAPIView):
    """
    Вью для отображения всех комментариев
    """
    model = GoalComment
    permission_classes = [CommentPermission]
    serializer_class = GoalCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal', ]
    ordering = ['-created', ]

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user_id=self.request.user.id
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    """
    Вью для работы с комментариями
    """
    model = GoalComment
    permission_classes = [CommentPermission]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user_id=self.request.user.id)


class BoardCreatedView(CreateAPIView):
    """
    Вью для создания досок
    """
    serializer_class = BoardCreateSerializer
    permission_classes = [BoardPermissions]

    def perform_create(self, serializer):
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardListView(ListAPIView):
    """
    Вью для отображения всех досок
    """
    serializer_class = BoardListSerializer
    permission_classes = [BoardPermissions]
    filter_backends = [OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.filter(participants__user_id=self.request.user.id, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    """
    Вью для работы с доской
    """
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.prefetch_related('participants__user').filter(is_deleted=False)

    def perform_destroy(self, instance: Board) -> None:
        with transaction.atomic():
            Board.objects.filter(id=instance.id).update(is_deleted=True)
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
