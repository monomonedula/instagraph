from abc_delegation import delegation_metaclass

from instagraph.gathering.lazy_insta_user import LazyInstaUser
from instagraph.gathering.interfaces import InstaUser


class RecursiveInstaUser(InstaUser, metaclass=delegation_metaclass("_target")):
    def __init__(self, user: InstaUser, actions):
        self._target = user
        self._actions = actions

    def save_followers(self):
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_followers()

    def save_following(self):
        self._target.save_following()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_following()

    def save_info(self):
        self._target.save_info()
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_info()

    def save_posts_info(self):
        self._target.save_posts_info()
        for f in self._target.retrieve_followers():
            LazyInstaUser(f, self._actions).save_posts_info()