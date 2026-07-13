from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemas import CreateConversation, SendMessage, ConversationResponse, ConversationsResponse, MessagesResponse
from models import  Conversation, Message, User
from logger import logger
from services.all_services import find_user, find_convo, get_current_user
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") #login endpoint

router = APIRouter()

@router.post('/conversations')
def create_conversation(convo: CreateConversation, token: str = Depends(oauth2_scheme) ,db = Depends(get_db)):
    current_user = get_current_user(token, db)

    if not current_user:
        raise HTTPException(status_code=404, detail="User not Found")
    

    db_convo = Conversation(title = convo.title, user_id = current_user.id)

    db.add(db_convo)
    db.commit()

    logger.info("Conversation Created Successfully")

    return {
        "Message": "Conversation Created Successfully"
    }




#work from here add current_user to each paths

@router.post('/conversations/{convo_id}/messages')
def send_message(convo_id: int, message: SendMessage, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_user = get_current_user(token, db)


    conversation = find_convo(convo_id, db)
    allowed_roles = {
        "user": "user",
        "assistant": "assistant",
        "system": "system"
    }

    role = allowed_roles.get(message.role)

    if not conversation:
        logger.error("Conversation Not Found")
        raise HTTPException(status_code=404, detail="Conversation Not Found")

    if not role:
        logger.warning("Invalid Role")
        raise HTTPException(status_code=400, detail="Invalid Role")


    db_message = Message(conversation_id = convo_id, role = message.role, content = message.content)
    
    db.add(db_message)
    db.commit()

    logger.info("Message Sent Successfully")

    return {
        "Message": "Message Sent Successfully"
    }







@router.get('/conversation/{convo_id}', response_model=ConversationResponse)
def get_conversation_history(convo_id: int, db = Depends(get_db)):
    conversation = find_convo(convo_id, db)

    if not conversation:
        logger.error("Conversation Not Found")
        raise HTTPException(status_code=404, detail="Conversation Not Found")

    
    logger.info("Success")
    return conversation

@router.get('/users/{user_id}/conversations', response_model=list[ConversationsResponse])
def list_user_conversations(user_id: int, db = Depends(get_db)):
    user = find_user(user_id, db)

    if not user:
        logger.error("User Not Found")
        raise HTTPException(status_code=404, detail="User Not Found")

    logger.info("Success")
    return db.query(Conversation).filter(Conversation.user_id == user.id).all()

@router.delete('/conversations/{convo_id}')
def delete_conversation(convo_id: int, db = Depends(get_db)):
    conversation = find_convo(convo_id, db)

    if not conversation:
        logger.error("Conversation Not Found")
        raise HTTPException(status_code=404, detail="Conversation Not Found")

    db.delete(conversation)
    db.commit()

    logger.info("Conversation Deleted Successful")
    return {
        "Message": "Conversation Deleted Successful"
    }

@router.get('/messages', response_model=list[MessagesResponse])
def search_message(search: str, db = Depends(get_db)):

    messages = db.query(Message).filter(Message.content.contains(search)).all()

    if not messages:
        logger.error("No Messages Found")
        raise HTTPException(status_code=404, detail="Messages Not Found")

    return messages

    


    

    



    






