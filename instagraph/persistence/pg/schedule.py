from instagraph.persistence.interfaces import FollowSchedule, User, Users, AlreadyFollowing
from instagraph.persistence.pg.pgsql import PgsqlBase


class PgFollowSchedule(FollowSchedule):
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
                " 'rejected' = ANY(tags)"
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
        if user.following().is_following(user):
            raise AlreadyFollowing(f"User {user.id()} is already following user {user_to_be_followed.id()}")
        self._pgsql.exec(
            "INSERT INTO follow_schedule (user_to_follow, user_to_be_followed, scheduled, priority, tags) "
            "VALUES (%s, %s, NOW()::date, %s, %s) ON CONFLICT DO NOTHING",
            (user.id(), user_to_be_followed.id(), priority, tags),
        )
