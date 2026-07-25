from models import Conversation, User
from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.caching import CacheService, CacheKeys
from schemas import ConversationsResponse
from datetime import datetime, UTC
from config import settings
import logging
from redis_client import redis

logger = logging.getLogger(__name__)

cache_service = CacheService(redis)

class RouterServiceConversation:

    @staticmethod
    def create_conversation_service(convo: Conversation, current_user: User, db: Session):
        db_convo = Conversation(title = convo.title, user_id = current_user.id, latest_activity = datetime.now(UTC))

        db.add(db_convo)
        db.commit()

        logger.info(
            "User '%s' Created a Conversation",
            current_user.username
        )

        cache_service.invalidate_cache_conversation(current_user.id)

    @staticmethod
    def rename_conversation_service(convo_id: int, new_title: str, current_user: User, db: Session):
        convo_in_user = ConversationService.find_convo_in_user(current_user, convo_id, db)
        
        convo_in_user.title = new_title.title

        db.commit()

        logger.info(
            "User '%s' Renamed Conversation '%s'",
            current_user.username, convo_id
        )

        cache_service.invalidate_cache_conversation(current_user.id)

    @staticmethod
    def delete_conversation_service(convo_id: int, current_user: User, db: Session):
        conversation = ConversationService.find_convo_in_user(current_user, convo_id, db)

        db.delete(conversation)
        db.commit()

        logger.info(
            "User '%s' Deleted Conversation id '%s'",
            current_user.username, 
            convo_id
        )

        cache_service.invalidate_cache_conversation(current_user.id)

class ConversationService:

    @staticmethod
    def find_convo_in_user(user: User, convo_id: int, db: Session):
        conversation = db.query(Conversation).filter(Conversation.user_id == user.id, Conversation.id == convo_id).first()
        if conversation is None:
            logging.warning(
                "User %s Doesnt have Conversation '%s'",
                user.username,
                convo_id
            )
            raise HTTPException(status_code=404, detail="User Doesnt have this Conversation")

        logger.info(
            "User '%s' Found the Message in Conversation '%s'",
            user.username,
            convo_id
        )
            
        return conversation

    @staticmethod
    def all_convo_in_user(user: User, page: int, db: Session):
        key = CacheKeys.all_conversation(user, page)

        cache = cache_service.get_cache(key)

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
        conversations = db.query(Conversation).filter(Conversation.user_id == user.id).order_by(Conversation.latest_activity.desc()).offset(offset).limit(convo_per_page).all()
    
        conversation_dict = [ConversationsResponse.model_validate(convo).model_dump()for convo in conversations] #turn python object into something json can understand its a list of convo so loop 

        cache_service.set_cache(key, conversation_dict)

        logger.info("User '%s' Retrieved the List of Conversation (page=%s)",
            user.username,
            page
        )

        return conversations