from typing import Callable

from methodtools import lru_cache

from instagraph.gathering.interfaces import InstaUser, InstaUserPosts
from instagraph.persistence.interfaces import User


class SimpleInstaUser(InstaUser):
    def __init__(
        self, bot,
        pg_user: User,
        make_user: Callable[[int], InstaUser],
        make_posts: Callable[[User], InstaUserPosts]
    ):
        self._bot = bot
        self._pg_user = pg_user
        self._make_user = make_user
        self._make_posts = make_posts

    def id(self):
        return self._pg_user.id()

    @lru_cache()
    def retrieve_followers(self):
        print("retrieve followers of %s" % self.id())
        return tuple(
            self._make_user(i)
            for i in self._bot.get_user_followers(self.id(), nfollows=2000)
        )

    @lru_cache()
    def retrieve_following(self):
        print("retrieve following of %s" % self.id())
        return tuple(
            self._make_user(i)
            for i in self._bot.get_user_following(self.id(), nfollows=1500)
        )

    def save_followers(self):
        print(f"saving followers of {self.id()}")
        self._pg_user.followers().update_followers(self.retrieve_followers())

    def save_following(self):
        print(f"saving following of {self.id()}")
        self._pg_user.following().update_following(self.retrieve_following())

    def save_info(self):
        print(f"saving info of {self.id()}")
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

    def save_posts_info(self):
        print(f"saving posts info of {self.id()}")
        for post in self._make_posts(self._pg_user).posts():
            post.update_caption()
            post.update_location()
            post.update_taken_at()
            post.update_likes()
            post.update_user_tags()