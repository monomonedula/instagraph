from instagraph.persistence.interfaces import User, AlreadyFollowing
from instagraph.persistence.pg.user_media import PgUserMedia
from instagraph.persistence.pg.user_info import PgUserInfo
from instagraph.persistence.pg.connections import PgUserFollowing, PgUserFollowers


class PgUser(User):
    def __init__(self, pgsql, id_):
        self._pgsql = pgsql
        self._id = id_

    def id(self):
        return self._id

    def following(self):
        return PgUserFollowing(self._pgsql, self._id)

    def followers(self):
        return PgUserFollowers(self._pgsql, self._id)

    def schedule_follow(self, user: User, tags=tuple(), priority=5):
        if self.following().is_following(user):
            raise AlreadyFollowing(f"Already following user {user.id()}")
        self._pgsql.exec(
            "INSERT INTO follow_schedule (user_to_follow, user_to_be_followed, scheduled, priority, tags) "
            "VALUES (%s, %s, NOW()::date, %s, %s) ON CONFLICT DO NOTHING",
            (self._id, user.id(), priority, tags),
        )

    def info(self) -> "UserInfo":
        return PgUserInfo(self._pgsql, self.id())

    def media(self) -> "UserMedia":
        return PgUserMedia(self._pgsql, self.id())