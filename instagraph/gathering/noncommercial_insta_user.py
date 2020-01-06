from instagraph.gathering.interfaces import InstaUser
from instagraph.persistence.pg.pgsql import PgsqlBase


class NonCommercialInstaUser(InstaUser):
    def __init__(self, pgsql: PgsqlBase, insta_user: InstaUser):
        self._pgsql = pgsql
        self._origin = insta_user

    def id(self) -> int:
        return self._origin.id()

    def save_followers(self):
        if not Skip(self._pgsql, self.id()).is_skipped():
            self._origin.save_followers()

    def save_following(self):
        if not Skip(self._pgsql, self.id()).is_skipped():
            self._origin.save_following()

    def save_info(self):
        if not Skip(self._pgsql, self.id()).is_skipped():
            self._origin.save_info()

    def save_posts_info(self):
        if not Skip(self._pgsql, self.id()).is_skipped():
            self._origin.save_posts_info()

    def retrieve_followers(self):
        if not Skip(self._pgsql, self.id()).is_skipped():
            return self._origin.retrieve_followers()
        return []

    def retrieve_following(self):
        if not Skip(self._pgsql, self.id()).is_skipped():
            return self._origin.retrieve_following()
        return []


class Skip:
    def __init__(self, pgsql, user_id):
        self._id = user_id
        self._pgsql = pgsql

    def is_skipped(self):
        ret = self._pgsql.exec(
            "SELECT tags FROM users WHERE id = %s",
            [self._id]
        )
        return ret and ("massfollower" in ret[0].tags or "commerce" in ret[0].tags)
