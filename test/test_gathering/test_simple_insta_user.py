from unittest.mock import patch, call

from instabot import Bot

from instagraph.gathering.simple_insta_user import SimpleInstaUser
from instagraph.persistence.interfaces import Locations, User
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
