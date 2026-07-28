import pytest
from fastapi import HTTPException
from services.conversation_service import RouterServiceConversation, ConversationService, CacheKeys
from models import Conversation
from unittest.mock import patch
from schemas import UpdateConversation

def test_create_conversation_service(fake_database):
    fake_db, fake_user =  fake_database

    fake_convo = Conversation(
        title="Fake_Title"
    )

    with patch("services.conversation_service.cache_service")as cache:

        RouterServiceConversation.create_conversation_service(fake_convo, fake_user, fake_db)


        fake_db.add.assert_called_once()
        fake_db.commit.assert_called_once()

        cache.invalidate_cache_conversation.assert_called_once_with(1)

        create_convo = fake_db.add.call_args.args[0] #gets the first argument added to the fake_db

        assert create_convo.title == "Fake_Title"
        assert create_convo.user_id == 1


def test_rename_conversation_service(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
            id=1,
            title="Old_Title"
        )

    fake_title = UpdateConversation(
        title="New_Title"
    )

    with patch("services.conversation_service.ConversationService.find_convo_in_user")as user, \
        patch("services.conversation_service.cache_service")as cache:

        user.return_value = fake_convo

        RouterServiceConversation.rename_conversation_service(1, fake_title, fake_user, fake_db)

        assert fake_convo.title == "New_Title"

        fake_db.commit.assert_called_once()

        user.assert_called_once_with(fake_user, 1, fake_db)
        cache.invalidate_cache_conversation.assert_called_once_with(1)

def test_delete_conversation_service(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
            title="Fake_Title"
        )

    with patch("services.conversation_service.ConversationService.find_convo_in_user")as user, \
        patch("services.conversation_service.cache_service")as cache:

        user.return_value = fake_convo
        
        RouterServiceConversation.delete_conversation_service(1, fake_user, fake_db)
        
        fake_db.delete.assert_called_once_with(fake_convo)
        fake_db.commit.assert_called_once()

        user.assert_called_once_with(fake_user, 1, fake_db)
        cache.invalidate_cache_conversation.assert_called_once_with(1)

def test_find_convo_in_user_success(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
        id=1,
        title="Fake_title"
    )

    fake_db.query.return_value.filter.return_value.first.return_value = fake_convo

    result = ConversationService.find_convo_in_user(fake_user, 1, fake_db)

    assert result == fake_convo
    fake_db.query.assert_called_once_with(Conversation)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_find_convo_in_user_failed(fake_database):
    fake_db, fake_user = fake_database

    fake_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException)as exc_info:
        ConversationService.find_convo_in_user(fake_user, 1, fake_db)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User Doesnt have this Conversation"
    fake_db.query.assert_called_once_with(Conversation)
    fake_db.query.return_value.filter.return_value.first.assert_called_once()

def test_all_convo_in_user_cache_miss(fake_database):
    fake_db, fake_user = fake_database

    fake_convos = [
        Conversation(id=1, title="A"),
        Conversation(id=2, title="B"),
    ]

    with patch("services.conversation_service.CacheKeys.all_conversation")as key, \
        patch("services.conversation_service.cache_service")as mock_cache:

        key.return_value = None

        mock_cache.get_cache.return_value = None

        fake_db.query.return_value\
                .filter.return_value\
                .order_by.return_value\
                .offset.return_value\
                .limit.return_value\
                .all.return_value = fake_convos

        result = ConversationService.all_convo_in_user(fake_user, 1, fake_db)

        assert result == fake_convos
        key.assert_called_once_with(fake_user, 1)
        mock_cache.get_cache.assert_called_once_with(None)
        fake_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.assert_called_once_with()
  
def test_all_convo_in_user_cache_hit(fake_database):
    fake_db, fake_user = fake_database

    with patch("services.conversation_service.CacheKeys.all_conversation")as key, \
            patch("services.conversation_service.cache_service")as mock_cache:
    
            key.return_value = None
    
            mock_cache.get_cache.return_value = "test_key"

            result = ConversationService.all_convo_in_user(fake_user, 1, fake_db)

            assert result == "test_key"
            key.assert_called_once_with(fake_user, 1)
            mock_cache.get_cache.assert_called_once_with(None)








    



    


        

        

  





        






