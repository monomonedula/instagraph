from methodtools import lru_cache

from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import User


class SmartInstaUser(InstaUser):
    def __init__(self, user: User, insta_user: InstaUser, bot, model):
        self._origin = insta_user
        self._bot = bot
        self._model = model
        self._user = user

    def id(self) -> int:
        return self._origin.id()

    def save_followers(self):
        if self._info_check():
            self._origin.save_followers()

    def save_following(self):
        if self._info_check():
            self._origin.save_following()

    def save_info(self):
        self._info_check()
        
    def save_posts_info(self):
        if self._info_check():
            self._origin.save_posts_info()

    def retrieve_followers(self):
        if self._info_check():
            return self._origin.retrieve_followers()
        return []

    def retrieve_following(self):
        if self._info_check():
            return self._origin.retrieve_following()
        return []

    @lru_cache()
    def _info_check(self):
        info = self._info()
        self._save_info(info)
        for tag in self._model.tags(info):
            self._user.info().add_tag(tag)
        is_target = self._model.is_target(info)
        if not is_target:
            print(f"user {self.id()} is not target. Skipping")
        else:
            print(f"user {self.id()} is target")
        return is_target

    def _save_info(self, info):
        self._user.info().update(
            name=info["full_name"],
            username=info["username"],
            nfollowers=info["follower_count"],
            nfollowing=info["following_count"],
            nposts=info["media_count"],
            bio=info["biography"],
            category=info.get("category"),
        )

    @lru_cache()
    def _info(self):
        return self._bot.get_user_info(self.id())
