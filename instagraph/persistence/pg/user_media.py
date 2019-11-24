from instagraph.persistence.interfaces import UserMedia
from instagraph.persistence.pg.post import PgPost


class PgUserMedia(UserMedia):
    def __init__(self, pgsql, user_id):
        self._pgsql = pgsql
        self._uid = user_id

    def post(self, post_id, url=None) -> "Post":
        self._pgsql.exec(
            "INSERT INTO posts (user_id, id, url) "
            "VALUES (%s) ON CONFLICT DO NOTHING",
            [self._uid, post_id, url]
        )
        return PgPost(self._pgsql, self._uid, post_id)