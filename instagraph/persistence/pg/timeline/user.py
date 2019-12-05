from instagraph.persistence.interfaces import User, UserMedia, UserInfo
from instagraph.persistence.pg.pgsql import PgsqlBase
from instagraph.persistence.pg.timeline.connections import (
    TimelineFollowers,
    TimelineFollowing,
)


class TimelinePgUser(User):
    def __init__(self, user: User, pgsql: PgsqlBase):
        self._user = user
        self._pgsql = pgsql

    def id(self):
        return self._user.id()

    def following(self):
        return TimelineFollowing(self._user.following(), self._pgsql)

    def followers(self):
        return TimelineFollowers(self._user.followers(), self._pgsql)

    def info(self) -> "UserInfo":
        return self._user.info()

    def media(self) -> "UserMedia":
        return self._user.media()
