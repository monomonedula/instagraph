from instagraph.gathering.simple_posts import SimpleInstaUserPosts
from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.interfaces import User, Users, Locations


class SimpleInstaUser(InstaUser):
    def __init__(self, bot, pg_user: User, pg_users: Users, pg_locations: Locations):
        self._bot = bot
        self._pg_user = pg_user
        self._pg_users = pg_users
        self._pg_locations = pg_locations
        self._followers = None
        self._following = None

    def id(self):
        return self._pg_user.id()

    def retrieve_followers(self):
        if self._followers is None:
            self._followers = tuple(
                SimpleInstaUser(self._bot, self._pg_users.user(i), self._pg_users, self._pg_locations)
                for i in self._bot.get_user_followers(self.id(), nfollows=20000)
            )
        return self._followers

    def retrieve_following(self):
        if self._following is None:
            self._following = tuple(
                SimpleInstaUser(self._bot, self._pg_users.user(i), self._pg_users, self._pg_locations)
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

    def save_posts_info(self):
        for post in SimpleInstaUserPosts(self._bot, self._pg_user, self._pg_users, self._pg_locations).posts():
            post.update_caption()
            post.update_location()
            post.update_taken_at()
            post.update_likes()
            post.update_user_tags()