from instagraph.persistence.interfaces import User, AlreadyFollowing, UserMedia, UserInfo
from instagraph.persistence.pg.pgsql import Pgsql
from instagraph.persistence.pg.timeline.connections import TimelineFollowers, TimelineFollowing


class TimelinePgUser(User):
    def __init__(self, user: User, pgsql: Pgsql):
        self._user = user
        self._pgsql = pgsql

    def id(self):
        return self._user.id()

    def following(self):
        return TimelineFollowing(self._user.following(), self._pgsql)

    def followers(self):
        return TimelineFollowers(self._user.followers(), self._pgsql)

    def schedule_follow(self, user, tags=tuple(), priority=5):
        if self._pgsql.exec(
            "SELECT * FROM connections_timeline "
            "WHERE follower = %s AND "
            "followed = %s",
            (self.id(), user.id()),
        ):
            raise AlreadyFollowing(f"Already following user {user.id()}")
        self._user.schedule_follow(user, tags, priority)

    def info(self) -> "UserInfo":
        return self._user.info()

    def media(self) -> "UserMedia":
        return self._user.media()
