from uuid import uuid4

from django.conf import settings
from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory

cat = []
new_goal = []


class Command(BaseCommand):
    help = "run bot"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)

    def handle_message(self, msg: Message):
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)
        if not tg_user.user:
            self.tg_client.send_message(msg.chat.id, "Подтвердите свой аккаунт")
            verification_code = str(uuid4())
            tg_user.verification_code = verification_code
            tg_user.save(update_fields=['verification_code'])
            self.tg_client.send_message(msg.chat.id, f'Verification_code - {verification_code}')
        else:
            self.handle_authorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        if msg.text.startswith('/'):
            self.handle_command(tg_user, msg.text)
        elif new_goal:
            new_cat = new_goal[0]
            new_goal.clear()
            cat.clear()
            Goal.objects.create(title=msg.text, category_id=new_cat, user=tg_user.user)
            self.tg_client.send_message(tg_user.chat_id, f'Создана цель {msg.text} в категории {new_cat}')
        else:
            self.tg_client.send_message(tg_user.chat_id, 'Неизвестная команда')

    def handle_command(self, tg_user: TgUser, command: str):
        match command:
            case '/goals':
                goals = Goal.objects.select_related('user').filter(user=tg_user.user, category__is_deleted=False
                                                                   ).exclude(status=Goal.Status.archived)
                if not goals:
                    self.tg_client.send_message(tg_user.chat_id, 'Нет целей')
                else:
                    resp = '\n'.join([goal.title for goal in goals])
                    self.tg_client.send_message(tg_user.chat_id, resp)
            case '/create':
                categories = GoalCategory.objects.select_related('user').filter(user=tg_user.user, is_deleted=False)
                if not categories:
                    self.tg_client.send_message(tg_user.chat_id, 'Нет категорий')
                else:
                    resp = 'Выберите категорию командой /{номер категории}'
                    for category in categories:
                        cat.append(str(category.id))
                        resp += '\n' + str(category.id) + ' ' + category.title
                    self.tg_client.send_message(tg_user.chat_id, resp)
            case _:
                if command[1:] in cat:
                    cat_command = command[1:]
                    new_goal.append(int(cat_command))
                    self.tg_client.send_message(tg_user.chat_id, f'Выбрана категория {cat_command}\n'
                                                                 f'Укажите название цели для создания')
                else:
                    self.tg_client.send_message(tg_user.chat_id, 'Нет такой категории')

    def handle(self, *args, **kwargs):
        offset = 0
        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)
