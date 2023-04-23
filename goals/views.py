from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from goals.filter import GoalDateFilter, CategoryBoardFilter
from goals.models import GoalCategory, Goal, GoalComment, BoardParticipant, Board
from goals.permissions import BoardPermissions, GoalCategoryPermissions, GoalBoardPermissions
from goals.serializers import GoalCreateSerializer, GoalCategorySerializer, GoalCategoryCreateSerializer, \
    GoalSerializer, GoalCommentCreateSerializer, GoalCommentSerializer, BoardCreateSerializer, BoardListSerializer, \
    BoardSerializer


class GoalCategoryCreateView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


class GoalCategoryListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
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
    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermissions]

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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalView(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, GoalBoardPermissions]
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
    permission_classes = [permissions.IsAuthenticated]
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
    model = GoalComment
    serializer_class = GoalCommentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal', ]
    ordering = ['-created', ]

    def get_queryset(self):
        return GoalComment.objects.filter(
            goal__category__board__participants__user_id=self.request.user.id
        )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentSerializer

    def get_queryset(self):
        return GoalComment.objects.filter(goal__category__board__participants__user_id=self.request.user.id)


class BoardCreatedView(CreateAPIView):
    serializer_class = BoardCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        BoardParticipant.objects.create(user=self.request.user, board=serializer.save())


class BoardLisrView(ListAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering = ['title']

    def get_queryset(self):
        return Board.objects.filter(participants__user_id=self.request.user.id, is_deleted=False)


class BoardView(RetrieveUpdateDestroyAPIView):
    permission_classes = [BoardPermissions]
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.prefetch_related('participants__user').filter(is_deleted=False)

    def perform_destroy(self, instance: Board) -> None:
        with transaction.atomic():
            Board.objects.filter(id=instance.id).update(is_deleted=True)
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
