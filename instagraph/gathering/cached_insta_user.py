from typing import Callable

from abc_delegation import delegation_metaclass

from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import User, Actions


class CachedInstaUser(InstaUser, metaclass=delegation_metaclass("_origin")):
    def __init__(self, user: InstaUser, db_user: User, actions: Actions,
                 make_user: Callable[[User], InstaUser]):
        self._origin = user
        self._db_user = db_user
        self._actions = actions
        self._make_user = make_user

    def id(self) -> int:
        return self._origin.id()

    def retrieve_followers(self):
        if self._actions.followers_explored(self.id()):
            return [self._make_user(u) for u in self._db_user.followers().users()]
        return self._origin.retrieve_followers()

    def retrieve_following(self):
        if self._actions.following_explored(self.id()):
            return [self._make_user(u) for u in self._db_user.following().users()]
        return self._origin.retrieve_following()
