from fastapi import APIRouter, Depends
from database import get_db
from schemas import CreateConversation, SendMessage, ConversationResponse, ConversationsResponse, MessagesResponse, EditMessage, UpdateConversation
from models import User
from services.message_service import RouterServiceMessage, MessageService
from services.conversation_service import RouterServiceConversation, ConversationService
from services.auth_service import get_current_user

router = APIRouter()

@router.post('/conversations')
def create_conversation(convo: CreateConversation, current_user: User = Depends(get_current_user) ,db = Depends(get_db)):
    
    RouterServiceConversation.create_conversation_service(convo, current_user, db)

    return {
        "Message": "Conversation Created Successfully"
    }

@router.put('/conversations/{convo_id}')
def rename_conversation(convo_id: int, new_title: UpdateConversation, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    RouterServiceConversation.rename_conversation_service(convo_id, new_title, current_user, db)

    return {
        "Message": "Title Renamed Successfully"
    }

@router.delete('/conversations/{convo_id}')
def delete_conversation(convo_id: int, current_user: User = Depends(get_current_user),db = Depends(get_db)):

    RouterServiceConversation.delete_conversation_service(convo_id, current_user, db)

    return {
        "Message": "Conversation Deleted Successfully"
    }

@router.post('/conversations/{convo_id}/messages')
def send_message(convo_id: int, message: SendMessage, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    RouterServiceMessage.send_message_service(convo_id, message, current_user, db)

    return {
        "Message": "Message Sent Successfully"
    }

@router.put('/conversations/{convo_id}/messages/{mess_id}')
def edit_message(convo_id: int, mess_id: int, new_message: EditMessage, current_user: User = Depends(get_current_user),db = Depends(get_db)):
    
    RouterServiceMessage.edit_message_service(convo_id, mess_id, new_message, current_user, db)

    return {
        "Message": "Message Updated Successfully"
    }

@router.get('/messages', response_model=list[MessagesResponse])
def search_messages(search: str, page: int = 1, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    
    messages = RouterServiceMessage.search_all_messages_service(current_user, search, page, db)

    return messages

@router.get('/conversation/{convo_id}', response_model=ConversationResponse)
def get_conversation_history(convo_id: int, page: int = 1, current_user: User = Depends(get_current_user),db = Depends(get_db)):

    conversation = MessageService.return_all_messages(current_user, convo_id, page, db)

    return conversation

@router.get('/conversations', response_model=list[ConversationsResponse])
def list_user_conversations(page: int = 1, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    conversations = ConversationService.all_convo_in_user(current_user, page, db)

    return conversations
