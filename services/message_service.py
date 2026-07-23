from models import Conversation, Message, User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from services.conversation_service import ConversationService
from datetime import datetime, UTC
from schemas import ConversationResponse, MessagesResponse, SendMessage, EditMessage
from services.caching import CacheService, CacheKeys
from config import settings
import logging

logger = logging.getLogger(__name__)

class RouterServiceMessage:

    @staticmethod
    def send_message_service(convo_id: int, message: SendMessage, current_user: User, db: Session):
        conversation = ConversationService.find_convo_in_user(current_user, convo_id, db)

        db_message = Message(conversation_id = convo_id, role = "user", content = message.content)

        conversation.latest_activity = datetime.now(UTC)

        db.add(db_message)
        db.commit()

        logger.info(
            "User '%s' Added a Message into Conversation '%s'",
            current_user.username,
            convo_id
        )

        CacheService.invalidate_cache_message(current_user.id, convo_id)
        CacheService.invalidate_cache_search(current_user.id)
        
    @staticmethod
    def edit_message_service(convo_id: int, mess_id: int, new_message: EditMessage, current_user: User, db: Session):
        conversation = ConversationService.find_convo_in_user(current_user, convo_id, db)

        message = MessageService.find_message(mess_id, conversation.id, db)
        
        message.content = new_message.content
        conversation.latest_activity = datetime.now(UTC)

        db.commit()

        logger.info(
            "User '%s' Edited Message'%s' in Conversation '%s'",
            current_user.username,
            mess_id,
            convo_id
        )

        CacheService.invalidate_cache_message(current_user.id, convo_id)
        CacheService.invalidate_cache_search(current_user.id)

    @staticmethod
    def search_all_messages_service(user: User, search: str, page: int, db: Session):
        key = CacheKeys.search_message(user, search, page)

        cache = CacheService.get_cache(key)

        if cache:
            logger.info(
                "Cache hit: %s",
                 key
            )
            return cache

        logger.info(
            "Cache miss: %s",
            key
        )
        

        convo_per_page = settings.CONVERSATION_PER_PAGE
        offset = (page - 1) * convo_per_page
        messages = db.query(Message).join(Message.conversation).filter(Message.content.contains(search), Conversation.user_id == user.id).order_by(Message.create_at.desc()).offset(offset).limit(convo_per_page).all()
        if not messages:
            raise HTTPException(status_code=404, detail='No Message Found')
        
        message_dict = [MessagesResponse.model_validate(mess).model_dump() for mess in messages]

        CacheService.set_cache(key, message_dict)

        logger.info(
                "User '%s' Searched: '%s' (page=%s)",
                user.username,
                search,
                page
            )

        return messages
    

class MessageService:

    @staticmethod 
    def find_message(mess_id: int, convo_id: int, db: Session):
        message = db.query(Message).filter(Message.conversation_id == convo_id, Message.id == mess_id).first()
        if message is None:
            logger.warning(
                "Message %s not Found in Conversation %s",
                mess_id,
                convo_id
            )
            raise HTTPException(status_code=404, detail='Message Not Found!')
        logger.info(
            "Message %s Found in Conversation %s",
            mess_id,
            convo_id
        )
        return message

    @staticmethod 
    def return_all_messages(user: User, convo_id: int, page: int, db: Session):

        key = CacheKeys.all_messages(user, convo_id, page)

        cache = CacheService.get_cache(key)

        if cache:
            logger.info(
                "Cache hit: %s",
                key
            )
            return cache

        logger.info(
            "Cache miss: %s",
            key
        )
        
        conversation =  db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo_id).first()

        if conversation is None:
            raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")
        
        convo_per_page = settings.CONVERSATION_PER_PAGE
        offset = (page - 1) * convo_per_page
        messages = db.query(Message).filter(Message.conversation_id == conversation.id).order_by(Message.latest_activity.desc()).offset(offset).limit(convo_per_page).all()

        conversation.messages = messages

        conversation_dict = ConversationResponse.model_validate(conversation).model_dump()

        CacheService.set_cache(key, conversation_dict)

        logger.info("User '%s' Retrieved history of Conversation '%s' (page=%s)", 
            user.username,
            convo_id, 
            page
        )

        return conversation

