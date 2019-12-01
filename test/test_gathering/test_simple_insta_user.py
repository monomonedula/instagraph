from unittest.mock import patch, call

import pytest
from instabot import Bot

from instagraph.gathering.simple_insta_user import SimpleInstaUser
from instagraph.persistence.interfaces import Locations, User
from instagraph.persistence.pg.locations import PgLocations
from instagraph.persistence.pg.pgsql import PgsqlBase
from instagraph.persistence.pg.users import PgUsers


class DummyPgsql(PgsqlBase):
    def exec(self, sql, args=None):
        raise NotImplemented

    def transaction(self, operation):
        raise NotImplemented


class DummyLocations(Locations):
    def location(self, pk):
        raise NotImplemented


class DummyUser(User):
    def __init__(self, id):
        self._id = id

    def id(self) -> int:
        return self._id

    def following(self):
        raise NotImplemented

    def followers(self):
        raise NotImplemented

    def schedule_follow(self, user_id, tags=tuple(), priority=5):
        raise NotImplemented

    def info(self):
        raise NotImplemented

    def media(self):
        raise NotImplemented


def test_simple_insta_user_retrieve_followers():
    """'
        'retrieve_followers' method should call the bot's 'get_user_followers' method
        return an iterable of users from id's yielded by 'get_user_followers'
    """
    bot = Bot()
    user = DummyUser(42)
    with patch.object(bot, "get_user_followers", return_value=(1, 2, 3, 4, 5)) as get_user_followers:
        users = PgUsers(DummyPgsql())
        dummy_follower = DummyUser(1337)
        with patch.object(users, "user", return_value=dummy_follower) as user_factory_method:
            locations = DummyLocations()
            followers = SimpleInstaUser(bot, user, users, locations).retrieve_followers()
    get_user_followers.assert_called_once_with(42, nfollows=20000)
    user_factory_method.assert_has_calls([call(i) for i in (1, 2, 3, 4, 5)])
    assert all(f.id() == dummy_follower.id() for f in followers)


def test_simple_insta_user_retrieve_following():
    """
        'retrieve_following' method should call the bot's 'get_user_following' method and
        return an iterable of users from id's yielded by 'get_user_following'.
        nfollows parameter is lower here because on Instagram it's usually the bots or
        commercial accounts who have more than 2000 following
    """
    bot = Bot()
    user = DummyUser(42)
    with patch.object(bot, "get_user_following", return_value=(1, 2, 3, 4, 5)) as get_user_following:
        users = PgUsers(DummyPgsql())
        dummy_follower = DummyUser(1337)
        with patch.object(users, "user", return_value=dummy_follower) as user_factory_method:
            locations = DummyLocations()
            followers = SimpleInstaUser(bot, user, users, locations).retrieve_following()
    get_user_following.assert_called_once_with(42, nfollows=2000)
    user_factory_method.assert_has_calls([call(i) for i in (1, 2, 3, 4, 5)])
    assert all(f.id() == dummy_follower.id() for f in followers)


@pytest.mark.postgresql
def test_simple_insta_user_save_following(pgsql):
    bot = Bot()
    users = PgUsers(pgsql)
    user = users.user(42)
    locations = PgLocations(pgsql)
    with patch.object(bot, "get_user_following", return_value=(234, 342, 555, 99, 100)) as get_user_following:
        SimpleInstaUser(bot, user, users, locations).save_following()
    assert set((u.id() for u in user.following().users())) == {234, 342, 555, 99, 100}
    get_user_following.assert_called_once_with(42, nfollows=2000)


@pytest.mark.integration
@pytest.mark.postgresql
def test_simple_insta_user_save_following(pgsql):
    bot = Bot()
    users = PgUsers(pgsql)
    user = users.user(42)
    locations = PgLocations(pgsql)
    with patch.object(bot, "get_user_followers", return_value=(234, 342, 555, 99, 100)) as get_user_followers:
        SimpleInstaUser(bot, user, users, locations).save_followers()
    assert set((u.id() for u in user.followers().users())) == {234, 342, 555, 99, 100}
    get_user_followers.assert_called_once_with(42, nfollows=20000)


@pytest.mark.integration
@pytest.mark.postgresql
def test_simple_insta_user_save_info(pgsql):
    bot = Bot()
    users = PgUsers(pgsql)
    user = users.user(42)
    locations = PgLocations(pgsql)
    with patch.object(
        bot,
        "get_user_info",
        return_value=dict(
            full_name="John",
            username="john_doe",
            follower_count=100,
            following_count=200,
            media_count=5,
            biography="Some bio text",
            category="some_category_tag",
        )
    ) as get_user_info:
        SimpleInstaUser(bot, user, users, locations).save_info()
    record = pgsql.exec("select * from users where id = 42")[0]
    assert record.username == "john_doe"
    assert record.name == "John"
    assert record.nfollowers == 100
    assert record.nfollows == 200
    assert record.posts_number == 5
    assert record.bio == "Some bio text"
    assert record.account_type == "some_category_tag"
    get_user_info.assert_called_once_with(42)
