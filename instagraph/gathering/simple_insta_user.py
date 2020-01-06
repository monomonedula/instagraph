from methodtools import lru_cache

from instagraph.gathering.simple_posts import SimpleInstaUserPosts
from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import User, Users, Locations


class SimpleInstaUser(InstaUser):
    def __init__(self, bot, pg_user: User, pg_users: Users, pg_locations: Locations):
        self._bot = bot
        self._pg_user = pg_user
        self._pg_users = pg_users
        self._pg_locations = pg_locations

    def id(self):
        return self._pg_user.id()

    @lru_cache()
    def retrieve_followers(self):
        print("retrieve followers of %s" % self.id())
        return tuple(
            SimpleInstaUser(self._bot, self._pg_users.user(i), self._pg_users, self._pg_locations)
            for i in self._bot.get_user_followers(self.id(), nfollows=2000)
        )

    @lru_cache()
    def retrieve_following(self):
        print("retrieve following of %s" % self.id())
        return tuple(
            SimpleInstaUser(self._bot, self._pg_users.user(i), self._pg_users, self._pg_locations)
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
        for post in SimpleInstaUserPosts(self._bot, self._pg_user, self._pg_users, self._pg_locations).posts():
            post.update_caption()
            post.update_location()
            post.update_taken_at()
            post.update_likes()
            post.update_user_tags()