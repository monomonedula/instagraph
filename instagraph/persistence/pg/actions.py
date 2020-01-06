from datetime import timedelta, datetime

from abc_delegation import delegation_metaclass

from instagraph.persistence.interfaces import Actions


class PgActions(Actions):
    # TODO: consider refactoring this into multiple classes. Too many methods
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def followers_explored(self, user_id):
        return bool(
            self._pgsql.exec(
                "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'followers_explored'",
                (user_id,),
            )
        )

    def following_explored(self, user_id):
        return bool(
            self._pgsql.exec(
                "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'following_explored'",
                (user_id,),
            )
        )

    def info_saved(self, user_id):
        return bool(
            self._pgsql.exec(
                "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'info_saved'",
                (user_id,),
            )
        )

    def mark_followers_explored(self, user_id):
        self._pgsql.exec(
            "INSERT INTO actions (date_taken, action_type, user_id) VALUES "
            "(NOW()::date, %s, %s)",
            ("followers_explored", user_id),
        )

    def mark_following_explored(self, user_id):
        self._pgsql.exec(
            "INSERT INTO actions (date_taken, action_type, user_id) VALUES "
            "(NOW()::date, %s, %s)",
            ("following_explored", user_id),
        )

    def mark_info_saved(self, user_id):
        self._pgsql.exec(
            "INSERT INTO actions (date_taken, action_type, user_id) VALUES "
            "(NOW()::date, %s, %s)",
            ("info_saved", user_id),
        )

    def mark_posts_info_saved(self, user_id):
        self._pgsql.exec(
            "INSERT INTO actions (date_taken, action_type, user_id) VALUES "
            "(NOW()::date, %s, %s)",
            ("posts_info_saved", user_id),
        )

    def posts_info_saved(self, user_id):
        return bool(
            self._pgsql.exec(
                "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'posts_info_saved'",
                (user_id,),
            )
        )


class PgActionsWithExpiration(Actions, metaclass=delegation_metaclass("_origin")):
    def __init__(self, pgsql, expiration_period: timedelta):
        self._expiration_period = expiration_period
        self._pgsql = pgsql
        self._origin = PgActions(pgsql)

    def followers_explored(self, user_id):
        rows = self._pgsql.exec(
            "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'followers_explored'"
            " ORDER BY date_taken DESC LIMIT 1",
            (user_id,),
        )
        return rows and rows[0].date_taken >= (datetime.today() - self._expiration_period).date()

    def following_explored(self, user_id):
        rows = self._pgsql.exec(
            "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'following_explored'"
            " ORDER BY date_taken DESC LIMIT 1",
            (user_id,),
        )
        return rows and rows[0].date_taken >= (datetime.today() - self._expiration_period).date()

    def info_saved(self, user_id):
        rows = self._pgsql.exec(
            "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'info_saved'"
            " ORDER BY date_taken DESC LIMIT 1",
            (user_id,),
        )
        return rows and rows[0].date_taken >= (datetime.today() - self._expiration_period).date()

    def posts_info_saved(self, user_id):
        rows = self._pgsql.exec(
            "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'posts_info_saved'"
            " ORDER BY date_taken DESC LIMIT 1",
            (user_id,),
        )
        return rows and rows[0].date_taken >= (datetime.today() - self._expiration_period).date()
