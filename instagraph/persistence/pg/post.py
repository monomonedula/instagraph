from datetime import datetime

from instagraph.persistence.interfaces import Post
from instagraph.persistence.pg.pgsql import Pgsql


class PgPost(Post):
    def __init__(self, pgsql: Pgsql, user_id, post_id: int):
        self._pgsql = pgsql
        self._id = post_id
        self._uid = user_id

    def update_caption(self, caption_text: str):
        self._pgsql.exec(
            "UPDATE posts SET caption = %s WHERE user_id = %s AND id = %s",
            (caption_text, self._uid, self._id),
        )

    def update_location(self, location):
        self._pgsql.exec(
            "UPDATE posts SET location = %s WHERE user_id = %s AND id = %s",
            (location.id(), self._uid, self._id),
        )

    def update_like_count(self, count):
        self._pgsql.exec(
            "UPDATE posts SET nlikes = %s WHERE user_id = %s AND id = %s",
            [count, self._uid, self._id],
        )

    def update_user_tags(self, users):
        for u in users:
            self._pgsql.exec(
                "INSERT INTO post_user_tags (user_id, post_id, post_user_id)"
                " VALUES (%s, %s, %s)"
                " ON CONFLICT DO NOTHING",
                [u.id(), self._id, self._uid],
            )

    def update_taken_at(self, dt: datetime):
        self._pgsql.exec(
            "UPDATE posts SET taken_at = %s WHERE user_id = %s AND id = %s",
            [dt, self._uid, self._id],
        )

    def update_likers(self, users):
        for u in users:
            self._pgsql.exec(
                "INSERT INTO likes (user_id, post_id, post_user_id)"
                " VALUES (%s, %s, %s)"
                " ON CONFLICT DO NOTHING",
                [u.id(), self._id, self._uid],
            )
        self.update_like_count(len(users))
