import requests
import logging

from bot.tg.dc import SendMessageResponse, GetUpdateResponse


class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdateResponse:

        url = self.get_url('getUpdates')
        params = {
            'offset': offset,
            'timeout': timeout
        }

        try:
            response = requests.get(url=url, params=params)
            return GetUpdateResponse(**response.json())
        except Exception as e:
            logging.error(
                'Status code: %d, Response: %s',
                response.status_code,
                str(response.json()),
            )
            logging.error('Не удалось получить обновления')
            raise e

    def send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url('sendMessage')
        data = {
            'chat_id': chat_id,
            'text': text
        }
        try:
            response = requests.post(url=url, data=data)
        except Exception as e:
            logging.error(
                'Status code: %d, Response: %s',
                response.status_code,
                str(response.json()),
            )
            logging.error('Не удалось отправить сообщение')
            raise e
        else:
            return SendMessageResponse(**response.json())
