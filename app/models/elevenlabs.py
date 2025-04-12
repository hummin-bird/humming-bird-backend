from pydantic import BaseModel


class ElevenLabsRequest(BaseModel):
    user_input: str
    session_id: str
