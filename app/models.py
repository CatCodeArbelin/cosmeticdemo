from pydantic import BaseModel


class IncomingMessage(BaseModel):
    source: str
    client_name: str
    message: str


class IncomingResult(BaseModel):
    ok: bool
    message_id: int
