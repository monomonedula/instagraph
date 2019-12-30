from instagraph.persistence.interfaces import UserMedia, Post
from instagraph.persistence.pg.post import PgPost


class PgUserMedia(UserMedia):
    def __init__(self, pgsql, user_id):
        self._pgsql = pgsql
        self._uid = user_id

    def post(self, post_id) -> "Post":
        self._pgsql.exec(
            "INSERT INTO posts (user_id, id) "
            "VALUES (%s, %s) ON CONFLICT DO NOTHING",
            [self._uid, post_id],
        )
        return PgPost(self._pgsql, self._uid, post_id)
