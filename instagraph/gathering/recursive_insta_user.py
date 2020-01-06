from typing import Callable

from abc_delegation import delegation_metaclass

from instagraph.gathering.lazy_insta_user import LazyInstaUser
from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import User


class RecursiveInstaUser(InstaUser, metaclass=delegation_metaclass("_target")):
    def __init__(
        self,
        user: InstaUser,
        user_factory: Callable[[User], InstaUser] = LazyInstaUser,
    ):
        self._target = user
        self._user = user_factory

    def save_followers(self):
        print(f"recursive save followers of {self.id()}")
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            print(f"inner recursive save followers of {f.id()}")
            self._user(f).save_followers()

    def save_following(self):
        print(f"recursive save following of {self.id()}")
        self._target.save_following()
        for f in self._target.retrieve_followers():
            print(f"inner recursive save following of {f.id()}")
            self._user(f).save_following()

    def save_info(self):
        print(f"recursive save info of {self.id()}")
        self._target.save_info()
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            print(f"inner recursive save info of {f.id()}")
            self._user(f).save_info()

    def save_posts_info(self):
        print(f"recursive save posts info of {self.id()}")
        self._target.save_posts_info()
        print(f"retreive followrs result {self._target.retrieve_followers()}")
        for f in self._target.retrieve_followers():
            print(f"inner recursive posts info of {f.id()}")
            self._user(f).save_posts_info()
