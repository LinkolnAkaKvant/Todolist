from django.contrib import admin

from goals.models import GoalCategory, Goal, GoalComment, Board


class GoalCategoryAdmin(admin.ModelAdmin):
    """
    Админка для категорий
    """
    list_display = ("title", "user", "created", "updated")
    search_fields = ("title", "user")


admin.site.register(GoalCategory, GoalCategoryAdmin)


class GoalAdmin(admin.ModelAdmin):
    """
    Админка для целей
    """
    list_display = ('title', 'user', 'created', 'updated')
    search_fields = ('title', 'description')


admin.site.register(Goal, GoalAdmin)


class GoalCommentAdmin(admin.ModelAdmin):
    """
    Админка для комментариев
    """
    list_display = ('user', 'text',)
    readonly_fields = ('created', 'updated',)


admin.site.register(GoalComment, GoalCommentAdmin)


class BoardAdmin(admin.ModelAdmin):
    """
    Админка для досок
    """
    list_display = ('title', 'is_deleted')
    readonly_fields = ('created', 'updated', )


admin.site.register(Board, BoardAdmin)
