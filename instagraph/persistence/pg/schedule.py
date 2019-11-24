from instagraph.persistence.interfaces import FollowSchedule
from instagraph.persistence.pg.user import PgUser


class PgFollowSchedule(FollowSchedule):
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def users_to_be_followed(self, by):
        return map(
            lambda record: PgUser(self._pgsql, record[0]),
            self._pgsql.exec(
                "SELECT user_to_be_followed FROM follow_schedule WHERE user_to_follow = %s "
                " ORDER BY priority ASC",
                (by,),
            ),
        )

    def mark_fulfilled(self, follower, followed):
        self._pgsql.exec(
            "UPDATE follow_schedule SET done = NOW()::date "
            "FROM ( SELECT * FROM follow_schedule"
            "        WHERE follower = %s AND followed = %s ORDER BY scheduled ASC LIMIT 1"
            "      )",
            (follower, followed),
        )
    # TODO: add follow rejection mechanism