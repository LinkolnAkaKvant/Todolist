import logging

from django.core.management import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import GoalCategory, Goal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.offset = 0

    def handle(self, *args, **options):
        logger.info('Bot start handling')
        while True:
            res = self.tg_client.get_updates(offset=self.offset)
            for item in res.result:
                self.offset = item.update_id + 1
                self.handle_message(item.message)

    def get_answer(self, chat_id):
        while True:
            res = self.tg_client.get_updates(offset=self.offset)
            for item in res.result:
                self.offset = item.update_id + 1
                answer = item.message.text
                if item.message.chat.id == chat_id:
                    return answer
                else:
                    self.handle_message(item.message)

    def create_goal(self, user, tg_user):
        categories = GoalCategory.objects.all()
        cat_text = ''
        for cat in categories:
            cat_text += f'{cat.id}: {cat.title} \n'

        self.tg_client.send_message(chat_id=tg_user.chat_id, text=f'Выберите категорию:\n{cat_text}')
        category = self.get_answer(tg_user.chat_id)

        self.tg_client.send_message(chat_id=tg_user.chat_id, text='Введите заголовок для цели')
        title = self.get_answer(tg_user.chat_id)

        result = Goal.objects.create(title=title, category=GoalCategory.objects.get(id=category), user=user, status=1,
                                     priority=1)
        return result.pk

    def handle_message(self, msg: Message):
        tg_user, created = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.user:
            self.handle_authorized(tg_user, msg)
            command = msg.text

            chat_id = tg_user.chat_id
            tg_user_model = TgUser.objects.get(chat_id=chat_id)
            user = tg_user_model.user

            if command == '/goals':
                data = Goal.objects.filter(user=user, status__in=[1, 2])
                goal_text = ''
                i = 1
                for goal in data:
                    goal_text += f'{i}. {goal.title}: {goal.description} \n'
                    i = i + 1
                self.tg_client.send_message(chat_id=tg_user.chat_id, text=f"Список ваших активных целей:\n{goal_text}")
            elif command == '/create':
                new_goal_id = self.create_goal(user, tg_user)
                self.tg_client.send_message(chat_id=tg_user.chat_id, text=f"Ваша цель №{new_goal_id} успешно создана!")
            else:
                self.tg_client.send_message(chat_id=tg_user.chat_id, text="Неизвестная команда")
        else:
            self.handle_unauthorized(tg_user, msg)

    def handle_unauthorized(self, tg_user: TgUser, msg: Message):
        self.tg_client.send_message(msg.chat.id, 'Hello')

        code = tg_user.set_verification_code()
        self.tg_client.send_message(tg_user.chat_id, f'You verification code: {code}')

    def handle_authorized(self, tg_user: TgUser, msg: Message):
        logger.info('Authorized')
