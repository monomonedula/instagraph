from abc_delegation import delegation_metaclass

from instagraph.persistence.interfaces import FollowSchedule, User, Users, AlreadyFollowing, Following, Followers
from instagraph.persistence.pg.pgsql import PgsqlBase


class PgFollowSchedule(FollowSchedule):
    # TODO: add unfollow scheduling functionality
    def __init__(self, pgsql: PgsqlBase, users: Users):
        self._pgsql = pgsql
        self._users = users

    def users_to_be_followed(self, by: User):
        return map(
            lambda record: self._users.user(record[0]),
            self._pgsql.exec(
                "SELECT user_to_be_followed FROM follow_schedule "
                " WHERE user_to_follow = %s AND"
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
            "      )",
            (follower.id(), followed.id()),
        )

    def mark_rejected(self, follower: User, followed: User, reason=None):
        query = " ".join(
            [
                "UPDATE follow_schedule ",
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
            raise AlreadyFollowing(f"User {user.id()} is already following user {user_to_be_followed.id()}")
        self._pgsql.exec(
            "INSERT INTO follow_schedule (user_to_follow, user_to_be_followed, scheduled, priority, tags) "
            "VALUES (%s, %s, NOW()::date, %s, %s)"
            " ON CONFLICT DO NOTHING",
            (user.id(), user_to_be_followed.id(), priority, list(tags)),
        )


class ScheduleConsistentUser(User, metaclass=delegation_metaclass("_user")):
    # TODO: write tests ScheduleConsistentUser
    def __init__(self, user: User, schedule: FollowSchedule, pgsql: PgsqlBase):
        self._user = user
        self._pgsql = pgsql
        self._schedule = schedule

    def following(self) -> "Following":
        return ScheduleConsFollowing(self._user.following(), self._schedule, self._pgsql)

    def followers(self) -> "Followers":
        pass


class ScheduleConsFollowing(Following, metaclass=delegation_metaclass("_following")):
    # TODO: write tests ScheduleConsistentFollowing
    def __init__(self, user: User, following: Following, schedule: FollowSchedule, pgsql):
        self._following = following
        self._schedule = schedule
        self._pgsql = pgsql
        self._user = user

    def users(self):
        return map(
            lambda u: ScheduleConsistentUser(u, self._schedule, self._pgsql),
            self._following.users()
        )

    def update_following(self, users):
        users = list(users)
        self._following.update_following(users)
        for u in users:
            self._schedule.mark_fulfilled(self._user, u)

    def follow(self, user):
        self._following.follow(user)
        self._schedule.mark_fulfilled(self._user, user)


class ScheduleConsFollowers(Followers, metaclass=delegation_metaclass("_followers")):
    def __init__(self, user: User, followers: Followers, schedule: FollowSchedule, pgsql):
        self._followers = followers
        self._schedule = schedule
        self._pgsql = pgsql
        self._user = user

    def users(self):
        return map(
            lambda u: ScheduleConsistentUser(u, self._schedule, self._pgsql),
            self._followers.users()
        )

    def update_followers(self, users):
        users = list(users)
        self._followers.update_followers(users)
        for u in users:
            self._schedule.mark_fulfilled(u, self._user)
