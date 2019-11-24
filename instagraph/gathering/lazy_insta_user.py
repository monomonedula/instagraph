from abc_delegation import delegation_metaclass

from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import Actions


class LazyInstaUser(InstaUser, metaclass=delegation_metaclass("_user")):
    def __init__(self, insta_user: InstaUser, actions: Actions):
        self._user = insta_user
        self._actions = actions

    def save_followers(self):
        if not self._actions.followers_explored(self.id()):
            self._user.save_followers()
            self._actions.mark_followers_explored(self.id())

    def save_following(self):
        if not self._actions.following_explored(self.id()):
            self._user.save_following()
            self._actions.mark_following_explored(self.id())

    def save_info(self):
        if not self._actions.info_saved(self.id()):
            self._user.save_info()
            self._actions.mark_info_saved(self.id())

    def save_posts_info(self):
        if not self._actions.posts_info_saved(self.id()):
            self._user.save_posts_info()
            self._actions.mark_posts_info_saved(self.id())