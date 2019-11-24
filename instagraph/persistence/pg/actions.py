from instagraph.persistence.interfaces import Actions


class PgActions(Actions):
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

    def media_info_saved(self, user_id):
        return bool(
            self._pgsql.exec(
                "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'media_info_saved'",
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
            ("media_info_saved", user_id),
        )

    def mark_posts_info_saved(self, user_id):
        self._pgsql.exec(
            "INSERT INTO actions (date_taken, action_type, user_id) VALUES "
            "(NOW()::date, %s, %s)",
            ("posts_info_saved", user_id)
        )

    def posts_info_saved(self, user_id):
        return bool(
            self._pgsql.exec(
                "SELECT date_taken FROM actions WHERE user_id = %s AND action_type = 'posts_info_saved'",
                (user_id,),
            )
        )
