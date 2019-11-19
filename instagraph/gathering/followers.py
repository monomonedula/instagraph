from abc import ABC, abstractmethod
from time import sleep

from ..persistence.actions import Actions
from ..persistence.users import User


class Scan:
    def __init__(self, target_user: "InstaUser"):
        self._target = target_user

    def run(self):
        self._target.save_info()
        self._target.save_followers()
        self._target.save_following()


class InstaUser(ABC):
    @abstractmethod
    def id(self) -> int:
        pass

    @abstractmethod
    def save_followers(self):
        pass

    @abstractmethod
    def save_following(self):
        pass

    @abstractmethod
    def save_info(self):
        pass

    @abstractmethod
    def retrieve_followers(self):
        pass

    @abstractmethod
    def retrieve_following(self):
        pass


class LazyInstaUser(InstaUser):
    def __init__(self, insta_user: InstaUser, actions: Actions):
        self._user = insta_user
        self._actions = actions

    def id(self) -> int:
        return self._user.id()

    def save_followers(self):
        if not self._actions.followers_explored(self._user.id()):
            self._user.save_followers()
            self._actions.mark_followers_explored(self._user.id())

    def save_following(self):
        if not self._actions.following_explored(self._user.id()):
            self._user.save_following()
            self._actions.mark_following_explored(self._user.id())

    def retrieve_followers(self):
        return self._user.retrieve_followers()

    def retrieve_following(self):
        return self._user.retrieve_following()

    def save_info(self):
        if not self._actions.info_saved(self._user.id()):
            sleep(5)
            self._user.save_info()
            self._actions.mark_info_saved(self._user.id())


class RecursiveInstaUser(InstaUser):
    def __init__(self, user: InstaUser, actions):
        self._target = user
        self._actions = actions

    def id(self):
        return self._target.id()

    def save_followers(self):
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_followers()

    def save_following(self):
        self._target.save_following()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_following()

    def retrieve_followers(self):
        return self._target.retrieve_followers()

    def retrieve_following(self):
        return self._target.retrieve_following()

    def save_info(self):
        self._target.save_info()
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_info()


class SimpleInstaUser(InstaUser):
    def __init__(self, bot, pg_user: User, pg_users):
        self._bot = bot
        self._pg_user = pg_user
        self._pg_users = pg_users
        self._followers = None
        self._following = None

    def id(self):
        return int(self._pg_user.id())

    def retrieve_followers(self):
        if self._followers is None:
            self._followers = tuple(
                SimpleInstaUser(self._bot, self._pg_users.user(i), self._pg_users)
                for i in self._bot.get_user_followers(self.id(), nfollows=20000)
            )
        return self._followers

    def retrieve_following(self):
        if self._following is None:
            self._following = tuple(
                SimpleInstaUser(self._bot, self._pg_users.user(i), self._pg_users)
                for i in self._bot.get_user_following(self.id(), nfollows=2000)
            )
        return self._following

    def save_followers(self):
        self._pg_user.followers().update_followers(self.retrieve_followers())

    def save_following(self):
        self._pg_user.following().update_following(self.retrieve_following())

    def save_info(self):
        info = self._bot.get_user_info(self.id())
        return self._pg_user.info().update(
            name=info["full_name"],
            username=info["username"],
            nfollowers=info["follower_count"],
            nfollowing=info["following_count"],
            nposts=info["media_count"],
            bio=info["biography"],
            category=info.get("category"),
        )
