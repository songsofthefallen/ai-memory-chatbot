import pytest
from services.message_service import RouterServiceMessage, MessageService
from unittest.mock import patch
from models import Conversation, Message
from schemas import SendMessage, EditMessage
from fastapi import HTTPException

def test_send_message_service_commit_succes(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
        id=1,
        title="fake_title",
        latest_activity="old time"
    )

    fake_message = SendMessage(
        content="fake_content"
    )

    with patch("services.message_service.ConversationService.find_convo_in_user")as convo, \
        patch("services.message_service.cache_service") as mock_service:

        convo.return_value = fake_convo

        RouterServiceMessage.send_message_service(1, fake_message, fake_user, fake_db)

        fake_db.add.assert_called_once()
        fake_db.commit.assert_called_once()

        convo.assert_called_once_with(fake_user, 1, fake_db)
        mock_service.invalidate_cache_message.assert_called_once_with(fake_user.id, 1)
        mock_service.invalidate_cache_search.assert_called_once_with(fake_user.id)

        send_message = fake_db.add.call_args.args[0]

        assert isinstance(send_message, Message)
        assert send_message.conversation_id == 1
        assert send_message.role == "user"
        assert send_message.content == "fake_content"
        assert fake_convo.latest_activity != "old_time"


def test_send_message_service_db_fail(fake_database):
        fake_db, fake_user = fake_database

        fake_message = SendMessage(
                content="fake_content"
            )

        fake_db.commit.side_effect = Exception("Database Error")

        with patch("services.message_service.ConversationService.find_convo_in_user"):

             with pytest.raises(Exception, match="Database Error"):
                  RouterServiceMessage.send_message_service(1, fake_message, fake_user, fake_db)

        fake_db.rollback.assert_called_once()

def test_edit_message_service_commit_success(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
            id=1,
            title="fake_title",
            latest_activity="old time"
        )

    fake_new_message = EditMessage(
         content="fake_new_message"
    )

    fake_old_message = Message(
         content="fake_old_message"
    )

    with patch("services.message_service.ConversationService.find_convo_in_user")as convo, \
        patch("services.message_service.MessageService.find_message")as message, \
        patch("services.message_service.cache_service") as mock_cache:

        convo.return_value = fake_convo
        message.return_value = fake_old_message

        RouterServiceMessage.edit_message_service(1, 1, fake_new_message, fake_user, fake_db)

        fake_db.commit.assert_called_once()

        convo.assert_called_once_with(fake_user, 1, fake_db)
        message.assert_called_once_with(1, 1, fake_db)
        mock_cache.invalidate_cache_message.assert_called_once_with(fake_user.id, 1)
        mock_cache.invalidate_cache_search.assert_called_once_with(fake_user.id)

    assert fake_old_message.content == "fake_new_message"
    assert fake_convo.latest_activity != "old time"

def test_edit_message_service_commit_fail(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
            id=1,
            title="fake_title",
            latest_activity="old time"
        )

    fake_new_message = EditMessage(
         content="fake_new_message"
    )

    fake_old_message = Message(
         content="fake_old_message"
    )

    fake_db.commit.side_effect = Exception("Database Error")

    with patch("services.message_service.ConversationService.find_convo_in_user")as convo, \
        patch("services.message_service.MessageService.find_message")as message:

        convo.return_value = fake_convo
        message.return_value = fake_new_message

        with pytest.raises(Exception, match="Database Error"):
            RouterServiceMessage.edit_message_service(1, 1, fake_old_message, fake_user, fake_db)
         
        fake_db.rollback.assert_called_once()

def test_search_all_messages_service_cache_miss(fake_database):
    fake_db, fake_user = fake_database

    fake_messages = [
            Message(
        id=1,
        conversation_id=1,
        role="user",
        content="fake_message1",
    ),
            Message(
        id=2,
        conversation_id=1,
        role="assistant",
        content="fake_message2",
    ),
]

    with patch("services.message_service.CacheKeys.search_message")as search, \
        patch("services.message_service.cache_service")as mock_cache:\

        search.return_value = None
        mock_cache.get_cache.return_value = None

        fake_db.query.return_value\
                .join.return_value\
                .filter.return_value\
                .order_by.return_value\
                .offset.return_value\
                .limit.return_value\
                .all.return_value = fake_messages

        result = RouterServiceMessage.search_all_messages_service(fake_user, "fake_search", 1, fake_db)

        assert isinstance(result[0], Message) #list of Message
        assert result == fake_messages
        search.assert_called_once_with(fake_user, "fake_search", 1)
        mock_cache.get_cache.assert_called_once_with(None)
        fake_db.query.return_value\
                        .join.return_value\
                        .filter.return_value\
                        .order_by.return_value\
                        .offset.return_value\
                        .limit.return_value\
                        .all.assert_called_once_with()
        

         
def test_search_all_messages_service_cache_hit(fake_database):
    fake_db, fake_user = fake_database

    fake_messages = [
            Message(
        id=1,
        conversation_id=1,
        role="user",
        content="fake_message1",
    ),
            Message(
        id=2,
        conversation_id=1,
        role="assistant",
        content="fake_message2",
    ),
]

    with patch("services.message_service.CacheKeys.search_message")as search, \
        patch("services.message_service.cache_service")as mock_cache:\

        search.return_value = None
        mock_cache.get_cache.return_value = "test_key"

        result = RouterServiceMessage.search_all_messages_service(fake_user, "fake_search", 1, fake_db)

        assert result == "test_key"
        search.assert_called_once_with(fake_user, "fake_search", 1)
        mock_cache.get_cache.assert_called_once_with(None)

def test_find_message_success(fake_database):
    fake_db, fake_user = fake_database

    fake_message = Message(
            id=1,
            conversation_id=1,
            role="user",
            content="fake_message1",
        )

    fake_db.query.return_value.filter.return_value.first.return_value = fake_message

    result = MessageService.find_message(1, 1, fake_db)

    assert isinstance(result, Message)
    assert result == fake_message
    fake_db.query.return_value.filter.return_value.first.assert_called_once_with()

def test_find_message_fail(fake_database):
    fake_db, _ = fake_database

    fake_message = Message(
            id=1,
            conversation_id=1,
            role="user",
            content="fake_message1",
        )

    fake_db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(HTTPException)as exc_info:
        MessageService.find_message(1, 1, fake_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == 'Message Not Found!'

def test_return_all_message_cache_miss(fake_database):
    fake_db, fake_user = fake_database

    fake_convo = Conversation(
                id=1,
                title="fake_title",
                latest_activity="old time",
                messages = []
            )

    fake_messages = [
                Message(
            id=1,
            conversation_id=1,
            role="user",
            content="fake_message1",
        ),
                Message(
            id=2,
            conversation_id=1,
            role="assistant",
            content="fake_message2",
        ),
    ]

    with patch("services.message_service.CacheKeys.all_messages")as key, \
        patch("services.message_service.cache_service")as mock_cache:

        key.return_value = None
        mock_cache.get_cache.return_value = None

        fake_db.query.return_value.filter.return_value.first.return_value = fake_convo
        fake_db.query.return_value\
                .filter.return_value\
                .order_by.return_value\
                .offset.return_value\
                .limit.return_value\
                .all.return_value = fake_messages

        result = MessageService.return_all_messages(fake_user, 1, 1, fake_db)

        assert isinstance(result, Conversation)
        assert result == fake_convo
        assert result.messages == fake_messages
        key.assert_called_once_with(fake_user, 1, 1)
        mock_cache.get_cache.assert_called_once_with(None)
        mock_cache.set_cache.assert_called_once()
        fake_db.query.return_value\
                        .filter.return_value\
                        .order_by.return_value\
                        .offset.return_value\
                        .limit.return_value\
                        .all.assert_called_once_with()

def test_return_all_message_cache_hit(fake_database):
    fake_db, fake_user = fake_database

    with patch("services.message_service.CacheKeys.all_messages")as key, \
        patch("services.message_service.cache_service")as mock_cache:

        key.return_value = None
        mock_cache.get_cache.return_value = "test_key"

        result = MessageService.return_all_messages(fake_user, 1, 1, fake_db)

        assert result == "test_key"
        key.assert_called_once_with(fake_user, 1, 1)
        mock_cache.get_cache.assert_called_once_with(None)




        


    
        

    


        



