from pydantic import BaseModel


class Chat(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    type: str | None = None


class Message(BaseModel):
    id: int
    is_bot: bool
    first_name: str
    last_name: str | None = None
    language_code: str | None = None


class UpdateObj(BaseModel):
    update_id: int
    message: Message


class GetUpdateResponse(BaseModel):
    ok: bool
    result: list[UpdateObj] = []


class SendMessageResponse(BaseModel):
    ok: bool
    result: Message = ''
