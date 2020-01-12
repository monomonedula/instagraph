from typing import Callable

from abc_delegation import delegation_metaclass

from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import Actions, User


class LazyInstaUser(InstaUser, metaclass=delegation_metaclass("_user")):
    def __init__(self, insta_user: InstaUser, actions: Actions, db_user: User):
        self._user = insta_user
        self._actions = actions
        self._db_user = db_user

    def id(self) -> int:
        return self._user.id()

    def save_followers(self):
        if not self._actions.followers_explored(self.id()):
            print(f"Lazy user: saving followers of {self.id()}")
            self._user.save_followers()
            self._actions.mark_followers_explored(self.id())
        else:
            print(f"Lazy user: skipping save followers of {self.id()}")

    def save_following(self):
        if not self._actions.following_explored(self.id()):
            print(f"Lazy user: saving following of {self.id()}")
            self._user.save_following()
            self._actions.mark_following_explored(self.id())
        else:
            print(f"Lazy user: skipping save following of {self.id()}")

    def save_info(self):
        if not self._actions.info_saved(self.id()):
            print(f"Lazy user: saving info of {self.id()}")
            self._user.save_info()
            self._actions.mark_info_saved(self.id())
        else:
            print(f"Lazy user: skipping save info of {self.id()}")

    def save_posts_info(self):
        if not self._actions.posts_info_saved(self.id()):
            print(f"Lazy user: saving posts info of {self.id()}")
            self._user.save_posts_info()
            self._actions.mark_posts_info_saved(self.id())
        else:
            print(f"Lazy user: skipping save posts info of {self.id()}")


class CachedLazyUser(InstaUser, metaclass=delegation_metaclass("_lazy_user")):
    def __init__(self, insta_user: InstaUser, actions: Actions, db_user: User,
                 make_insta_user: Callable[[User], InstaUser]):
        self._lazy_user = LazyInstaUser(
            insta_user=insta_user,
            actions=actions,
            db_user=db_user
        )
        self._make_user = make_insta_user
        self._db_user = db_user

    def retrieve_followers(self):
        print("cached user retreiving followers")
        self.save_followers()
        return [self._make_user(u) for u in self._db_user.followers().users()]

    def retrieve_following(self):
        print("cached user retreiving following")
        self.save_following()
        return [self._make_user(u) for u in self._db_user.following().users()]
