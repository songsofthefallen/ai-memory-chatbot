from fastapi import APIRouter, Depends
from database import get_db
from schemas import CreateConversation, SendMessage, ConversationResponse, ConversationsResponse, MessagesResponse, EditMessage, UpdateConversation
from models import  Conversation, Message, User
from logger import logger
from services.message_service import search_all_messages, find_message, return_all_messages
from services.conversation_service import find_convo_in_user, all_convo_in_user
from services.auth_service import get_current_user
from datetime import datetime, UTC




router = APIRouter()

@router.post('/conversations')
def create_conversation(convo: CreateConversation, current_user: User = Depends(get_current_user) ,db = Depends(get_db)):
    db_convo = Conversation(title = convo.title, user_id = current_user.id, latest_activity = datetime.now(UTC))

    db.add(db_convo)
    db.commit()

    logger.info("Conversation Created Successfully")

    return {
        "Message": "Conversation Created Successfully"
    }

@router.put('/conversations/{convo_id}')
def rename_conversation(convo_id: int, new_title: UpdateConversation, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    convo_in_user = find_convo_in_user(current_user, convo_id, db)
    
    convo_in_user.title = new_title.title

    db.commit()

    logger.info("Conversation Renamed Successfully")

    return {
        "Message": "Title Sent Successfully"
    }


@router.post('/conversations/{convo_id}/messages')
def send_message(convo_id: int, message: SendMessage,current_user: User = Depends(get_current_user), db = Depends(get_db)):

    conversation = find_convo_in_user(current_user, convo_id, db)

    db_message = Message(conversation_id = convo_id, role = "user", content = message.content)

    conversation.latest_activity = datetime.now(UTC)

    
    
    db.add(db_message)
    db.commit()

    logger.info("Message Sent Successfully")

    return {
        "Message": "Message Sent Successfully"
    }

@router.put('/conversations/{convo_id}/messages/{mess_id}')
def edit_message(convo_id: int, mess_id: int, new_message: EditMessage, current_user: User = Depends(get_current_user),db = Depends(get_db)):
    
    conversation = find_convo_in_user(current_user, convo_id, db)

    message = find_message(mess_id, conversation.id, db)
    
    message.content = new_message.content
    conversation.latest_activity = datetime.now(UTC)

    db.commit()

    logger.info("Message Edited Successfully")

    return {
        "Message": "Message Updated Successfully"
    }

@router.get('/conversation/{convo_id}', response_model=ConversationResponse)
def get_conversation_history(convo_id: int, page: int = 1, current_user: User = Depends(get_current_user),db = Depends(get_db)):

    conversation = return_all_messages(current_user, convo_id, page, db)

    
    logger.info("Success")
    return conversation

@router.get('/conversations', response_model=list[ConversationsResponse])
def list_user_conversations(page: int = 1, current_user: User = Depends(get_current_user), db = Depends(get_db)):

    conversations = all_convo_in_user(current_user, page, db)

    return conversations

@router.delete('/conversations/{convo_id}')
def delete_conversation(convo_id: int, current_user: User = Depends(get_current_user),db = Depends(get_db)):

    conversation = find_convo_in_user(current_user, convo_id, db)

    db.delete(conversation)
    db.commit()

    logger.info("Conversation Deleted Successful")
    return {
        "Message": "Conversation Deleted Successful"
    }



@router.get('/messages', response_model=list[MessagesResponse])
def search_messages(search: str, page: int = 1, current_user: User = Depends(get_current_user), db = Depends(get_db)):
    messages = search_all_messages(current_user, search, page, db)

    return messages

    


    

    



    






