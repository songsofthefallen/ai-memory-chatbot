from fastapi import APIRouter, Depends
from database import get_db
from schemas import CreateConversation, SendMessage, ConversationResponse, ConversationsResponse, MessagesResponse, EditMessage, UpdateConversation
from models import User
from logger import logger
from services.message_service import search_all_messages, send_message, edit_message, return_all_messages
from services.conversation_service import create_conversation, delete_conversation, all_convo_in_user
from services.auth_service import get_current_user

router = APIRouter()

@router.post('/conversations')
def create_conversation(convo: CreateConversation, current_user: User = Depends(get_current_user) ,db = Depends(get_db)):
    
    create_conversation(convo, current_user, db)

    logger.info("Conversation Created Successfully")

    return {
        "Message": "Conversation Created Successfully"
    }

@router.put('/conversations/{convo_id}')
def rename_conversation(convo_id: int, new_title: UpdateConversation, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    rename_conversation(convo_id, new_title, current_user, db)

    logger.info("Conversation Renamed Successfully")

    return {
        "Message": "Title Sent Successfully"
    }

@router.delete('/conversations/{convo_id}')
def delete_conversation(convo_id: int, current_user: User = Depends(get_current_user),db = Depends(get_db)):

    delete_conversation(convo_id, current_user, db)

    logger.info("Conversation Deleted Successful")
    return {
        "Message": "Conversation Deleted Successful"
    }



@router.post('/conversations/{convo_id}/messages')
def send_message(convo_id: int, message: SendMessage, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    send_message(convo_id, message, current_user, db)

    logger.info("Message Sent Successfully")

    return {
        "Message": "Message Sent Successfully"
    }

@router.put('/conversations/{convo_id}/messages/{mess_id}')
def edit_message(convo_id: int, mess_id: int, new_message: EditMessage, current_user: User = Depends(get_current_user),db = Depends(get_db)):
    
    edit_message(convo_id, mess_id, new_message, current_user, db)

    logger.info("Message Edited Successfully")

    return {
        "Message": "Message Updated Successfully"
    }

@router.get('/messages', response_model=list[MessagesResponse])
def search_messages(search: str, page: int = 1, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    messages = search_all_messages(current_user, search, page, db)

    return messages


@router.get('/conversation/{convo_id}', response_model=ConversationResponse)
def get_conversation_history(convo_id: int, page: int = 1, current_user: User = Depends(get_current_user),db = Depends(get_db)):

    conversation = return_all_messages(current_user, convo_id, page, db)

    logger.info("Success")
    return conversation

@router.get('/conversations', response_model=list[ConversationsResponse])
def list_user_conversations(page: int = 1, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    conversations = all_convo_in_user(current_user, page, db)

    return conversations





    


    

    



    






