from instagraph.persistence.interfaces import Users
from instagraph.persistence.pg.user import PgUser
from instagraph.persistence.pg.pgsql import PgsqlBase


class PgUsers(Users):
    def __init__(self, pgsql: PgsqlBase):
        self._pgsql = pgsql

    def user(
        self, user_id,
    ):
        self._pgsql.exec(
            "INSERT INTO users (id) " "VALUES (%s) ON CONFLICT DO NOTHING", [user_id]
        )
        return PgUser(self._pgsql, user_id, self)
