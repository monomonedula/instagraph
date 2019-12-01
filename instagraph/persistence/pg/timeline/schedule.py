from typing import Iterable

from instagraph.persistence.interfaces import FollowSchedule, User
from instagraph.persistence.pg.pgsql import PgsqlBase

from abc_delegation import *

from instagraph.persistence.pg.timeline.user import TimelinePgUser


class TimelineSchedule(FollowSchedule, metaclass=delegation_metaclass(delegate_attr="_schedule")):
    def __init__(self, schedule: FollowSchedule, pgsql: PgsqlBase):
        self._pgsql = pgsql
        self._schedule = schedule

    def users_to_be_followed(self, by: User) -> Iterable[User]:
        return map(
            lambda user: TimelinePgUser(user, self._pgsql),
            self._schedule.users_to_be_followed(by)
        )

    def add_record(self, user, user_to_be_followed, tags=tuple(), priority=5):
        self._schedule.add_record(user, user_to_be_followed, tags, priority)


class NoFollowDuplications(FollowSchedule, metaclass=delegation_metaclass(delegate_attr="_schedule")):
    def __init__(self, schedule: FollowSchedule, pgsql: PgsqlBase):
        self._pgsql = pgsql
        self._schedule = schedule

    def add_record(self, user: User, user_to_be_followed: User, tags: tuple = None, priority: int = None):
        if self._pgsql.exec(
                "SELECT * FROM connections_timeline "
                "WHERE follower = %s AND "
                "followed = %s",
                (user.id(), user_to_be_followed.id()),
        ):
            raise HadBeenFollowing(f"User {user.id()} has history of following user {user_to_be_followed.id()}")


class HadBeenFollowing(Exception):
    pass
