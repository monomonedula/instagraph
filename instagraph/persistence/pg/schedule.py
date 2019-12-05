from typing import Iterable

from abc_delegation import delegation_metaclass

from instagraph.persistence.interfaces import (
    FollowSchedule,
    User,
    Users,
    AlreadyFollowing,
    Following,
    Followers,
    UnfollowSchedule,
    AlreadyNotFollowing,
)
from instagraph.persistence.pg.pgsql import PgsqlBase


class PgUnfollowSchedule(UnfollowSchedule):
    def __init__(self, pgsql: PgsqlBase, users: Users):
        self._pgsql = pgsql
        self._users = users

    def users_to_be_unfollowed(self, by: User) -> Iterable[User]:
        return map(
            lambda record: self._users.user(record[0]),
            self._pgsql.exec(
                "SELECT unfollowed FROM unfollow_schedule "
                " WHERE follower = %s AND"
                " done IS NULL AND"
                " NOT ('rejected' = ANY(tags))"
                " ORDER BY priority ASC",
                (by.id(),),
            ),
        )

    def mark_fulfilled(self, follower: User, unfollowed: User):
        return self._pgsql.exec(
            "UPDATE unfollow_schedule SET done = NOW()::date "
            "FROM (SELECT * FROM unfollow_schedule"
            "        WHERE follower = %s AND unfollowed = %s ORDER BY scheduled ASC LIMIT 1) as foo",
            (follower.id(), unfollowed.id()),
        )

    def mark_rejected(self, follower: User, unfollowed: User, reason=None):
        query = " ".join(
            [
                "UPDATE unfollow_schedule SET",
                "tags = array_append(array_remove(tags, %s), %s)"
                if not reason
                else "tags = array_append(array_remove(array_append(array_remove(tags, %s), %s), %s) %s)",
                " WHERE follower = %s AND unfollowed = %s",
            ]
        )
        self._pgsql.exec(
            query,
            [
                "rejected",
                "rejected",
                *([reason, reason] if reason else []),
                follower.id(),
                unfollowed.id(),
            ],
        )

    def add_record(
        self,
        user: User,
        user_to_be_unfollowed: User,
        tags: tuple = tuple(),
        priority: int = None,
    ):
        if not user.following().is_following(user_to_be_unfollowed):
            raise AlreadyNotFollowing(
                f"User {user.id()} is not following user {user_to_be_unfollowed.id()}"
            )
        self._pgsql.exec(
            "INSERT INTO unfollow_schedule (follower, unfollowed, scheduled, priority, tags) "
            "VALUES (%s, %s, NOW()::date, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (user.id(), user_to_be_unfollowed.id(), priority, list(tags)),
        )


class PgFollowSchedule(FollowSchedule):
    def __init__(self, pgsql: PgsqlBase, users: Users):
        self._pgsql = pgsql
        self._users = users

    def users_to_be_followed(self, by: User):
        return map(
            lambda record: self._users.user(record[0]),
            self._pgsql.exec(
                "SELECT followed FROM follow_schedule "
                " WHERE follower = %s AND"
                " done IS NULL AND"
                " NOT ('rejected' = ANY(tags))"
                " ORDER BY priority ASC",
                (by.id(),),
            ),
        )

    def mark_fulfilled(self, follower: User, followed: User):
        self._pgsql.exec(
            "UPDATE follow_schedule SET done = NOW()::date "
            "FROM ( SELECT * FROM follow_schedule"
            "        WHERE follower = %s AND followed = %s ORDER BY scheduled ASC LIMIT 1"
            "      ) as foo",
            (follower.id(), followed.id()),
        )

    def mark_rejected(self, follower: User, followed: User, reason=None):
        query = " ".join(
            [
                "UPDATE follow_schedule SET",
                "tags = array_append(array_remove(tags, %s), %s)"
                if not reason
                else "tags = array_append(array_remove(array_append(array_remove(tags, %s), %s), %s) %s)",
                " WHERE follower = %s AND followed = %s",
            ]
        )
        self._pgsql.exec(
            query,
            [
                "rejected",
                "rejected",
                *([reason, reason] if reason else []),
                follower.id(),
                followed.id(),
            ],
        )

    def add_record(self, user, user_to_be_followed, tags=tuple(), priority=5):
        if user.following().is_following(user_to_be_followed):
            raise AlreadyFollowing(
                f"User {user.id()} is already following user {user_to_be_followed.id()}"
            )
        self._pgsql.exec(
            "INSERT INTO follow_schedule (follower, followed, scheduled, priority, tags) "
            "VALUES (%s, %s, NOW()::date, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (user.id(), user_to_be_followed.id(), priority, list(tags)),
        )

    def clean_up(self, target="fulfilled"):
        # TODO: add a record removal method
        pass


class ScheduleConsistentUser(User, metaclass=delegation_metaclass("_user")):
    # TODO: write tests ScheduleConsistentUser
    def __init__(
        self,
        user: User,
        follow_schedule: FollowSchedule,
        unfollow_schedule: UnfollowSchedule,
        pgsql: PgsqlBase,
    ):
        self._user = user
        self._pgsql = pgsql
        self._follow_schedule = follow_schedule
        self._unfollow_schedule = unfollow_schedule

    def following(self) -> "Following":
        return ScheduleConsFollowing(
            self,
            self._user.following(),
            self._follow_schedule,
            self._unfollow_schedule,
            self._pgsql,
        )

    def followers(self) -> "Followers":
        return ScheduleConsFollowers(
            self,
            self._user.followers(),
            self._follow_schedule,
            self._unfollow_schedule,
            self._pgsql,
        )


class ScheduleConsFollowing(Following, metaclass=delegation_metaclass("_following")):
    # TODO: write tests ScheduleConsistentFollowing
    def __init__(
        self,
        user: User,
        following: Following,
        follow_schedule: FollowSchedule,
        unfollow_schedule: UnfollowSchedule,
        pgsql: PgsqlBase,
    ):
        self._following = following
        self._follow_schedule = follow_schedule
        self._unfollow_schedule = unfollow_schedule
        self._pgsql = pgsql
        self._user = user

    def users(self):
        return map(
            lambda u: ScheduleConsistentUser(
                u, self._follow_schedule, self._unfollow_schedule, self._pgsql
            ),
            self._following.users(),
        )

    def update_following(self, users):
        users = list(users)
        self._following.update_following(users)
        for u in users:
            self._follow_schedule.mark_fulfilled(self._user, u)
        # TODO: mark all unfollow records as fulfilled for users not present

    def follow(self, user):
        self._following.follow(user)
        self._follow_schedule.mark_fulfilled(self._user, user)

    def unfollow(self, user):
        self._following.unfollow(user)
        self._unfollow_schedule.mark_fulfilled(self._user, user)

    def clean_up(self, target="fulfilled"):
        # TODO: implement unactive records removal
        pass


class ScheduleConsFollowers(Followers, metaclass=delegation_metaclass("_followers")):
    def __init__(
        self,
        user: User,
        followers: Followers,
        follow_schedule: FollowSchedule,
        unfollow_schedule: UnfollowSchedule,
        pgsql: PgsqlBase,
    ):
        self._followers = followers
        self._follow_schedule = follow_schedule
        self._unfollow_schedule = unfollow_schedule
        self._pgsql = pgsql
        self._user = user

    def users(self):
        return map(
            lambda u: ScheduleConsistentUser(
                u, self._follow_schedule, self._unfollow_schedule, self._pgsql
            ),
            self._followers.users(),
        )

    def update_followers(self, users):
        users = list(users)
        self._followers.update_followers(users)
        for u in users:
            self._follow_schedule.mark_fulfilled(u, self._user)
