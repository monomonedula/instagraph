from instagraph.persistence.interfaces import User, AlreadyFollowing, UserInfo, UserMedia, Users
from instagraph.persistence.pg.pgsql import PgsqlBase
from instagraph.persistence.pg.user_media import PgUserMedia
from instagraph.persistence.pg.user_info import PgUserInfo
from instagraph.persistence.pg.connections import PgUserFollowing, PgUserFollowers


class PgUser(User):
    def __init__(self, pgsql: PgsqlBase, id_: int, users: Users):
        self._pgsql = pgsql
        self._id = id_
        self._users = users

    def id(self):
        return self._id

    def following(self):
        return PgUserFollowing(self._pgsql, self._id, self._users)

    def followers(self):
        return PgUserFollowers(self._pgsql, self._id, self._users)

    def info(self) -> "UserInfo":
        return PgUserInfo(self._pgsql, self.id())

    def media(self) -> "UserMedia":
        return PgUserMedia(self._pgsql, self.id())