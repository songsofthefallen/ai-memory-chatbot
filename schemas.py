from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginUser(BaseModel):
    username: str
    password: str

class CreateConversation(BaseModel):
    title: str

class SendMessage(BaseModel):
    content: str

class ConversationResponse(BaseModel): #with message
    id: int
    title: str
    messages: Optional[list[MessageResponse]] = None

    model_config = {
        "from_attributes": True
    }

class ConversationsResponse(BaseModel): #without for like a sidebar
    id: int
    title: str

    model_config = {
        "from_attributes": True
    }


class MessageResponse(BaseModel):
    role: str
    content: str

    model_config = {
        "from_attributes": True
    }

class MessagesResponse(BaseModel):
    conversation_id: int
    role: str
    content: str

    model_config = {
        "from_attributes": True
    }


