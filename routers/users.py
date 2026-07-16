from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemas import CreateConversation, SendMessage, ConversationResponse, ConversationsResponse, MessagesResponse, EditMessage, UpdateConversation
from models import  Conversation, Message
from logger import logger
from services.all_services import  get_current_user, find_convo_in_user, all_convo_in_user, get_all_messages, find_message, return_all_messages
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") #login endpoint

router = APIRouter()

@router.post('/conversations')
def create_conversation(convo: CreateConversation, token: str = Depends(oauth2_scheme) ,db = Depends(get_db)):
    current_user = get_current_user(token, db)

    

    db_convo = Conversation(title = convo.title, user_id = current_user.id)

    db.add(db_convo)
    db.commit()

    logger.info("Conversation Created Successfully")

    return {
        "Message": "Conversation Created Successfully"
    }

@router.put('/conversations/{convo_id}')
def rename_conversation(convo_id: int, new_title: UpdateConversation, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_user = get_current_user(token, db)

    
    convo_in_user = find_convo_in_user(current_user, convo_id, db)

    if convo_in_user is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    
    convo_in_user.title = new_title

    db.commit()

    return {
        "Message": "Title Sent Successfully"
    }


@router.post('/conversations/{convo_id}/messages')
def send_message(convo_id: int, message: SendMessage, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_user = get_current_user(token, db)

    
    convo_in_user = find_convo_in_user(current_user, convo_id, db)

    if convo_in_user is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")

    db_message = Message(conversation_id = convo_id, role = "user", content = message.content)
    
    db.add(db_message)
    db.commit()

    logger.info("Message Sent Successfully")

    return {
        "Message": "Message Sent Successfully"
    }

@router.put('/conversations/{convo_id}/messages/{mess_id}')
def edit_message(convo_id: int, mess_id: int, new_message: EditMessage, token: str = Depends(oauth2_scheme),db = Depends(get_db)):
    current_user = get_current_user(token, db)


    
    convo_in_user = find_convo_in_user(current_user, convo_id, db)

    if convo_in_user is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    
    message = find_message(mess_id, db)

    if message is None:
        raise HTTPException(status_code=404, detail='Message Not Found!')
    
    message.content = new_message.content

    db.commit()

    return {
        "Message": "Message Updated Successfully"
    }
    
    
    

    

    













@router.get('/conversation/{convo_id}', response_model=ConversationResponse)
def get_conversation_history(convo_id: int, page: int = 1, token: str = Depends(oauth2_scheme),db = Depends(get_db)):
    current_user = get_current_user(token, db)



    conversation = return_all_messages(current_user, convo_id, page, db)

    if conversation is None:
        logger.error("Conversation Not Found")
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    
    logger.info("Success")
    return conversation











@router.get('/conversations', response_model=list[ConversationsResponse])
def list_user_conversations(page: int = 1, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_user = get_current_user(token, db)


    
    conversations = all_convo_in_user(current_user, page, db)

    if conversations is None:
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
    
    
    return conversations








@router.delete('/conversations/{convo_id}')
def delete_conversation(convo_id: int, token: str = Depends(oauth2_scheme),db = Depends(get_db)):
    current_user = get_current_user(token, db)



    conversation = find_convo_in_user(current_user, convo_id, db)

    if conversation is None:
        logger.error("Conversation Not Found")
        raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")

    db.delete(conversation)
    db.commit()

    logger.info("Conversation Deleted Successful")
    return {
        "Message": "Conversation Deleted Successful"
    }



@router.get('/messages', response_model=list[MessagesResponse])
def search_messages(search: str, page: int = 1, token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    current_user = get_current_user(token, db)


    messages = get_all_messages(current_user, search, page, db)

    if not messages:
        logger.error("No Messages Found")
        raise HTTPException(status_code=404, detail="Messages Not Found")

    return messages

    


    

    



    






