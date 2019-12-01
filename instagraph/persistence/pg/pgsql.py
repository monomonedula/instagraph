from abc import ABC, abstractmethod

from psycopg2.extras import NamedTupleConnection
from psycopg2.pool import ThreadedConnectionPool
from psycopg2 import ProgrammingError


class PgsqlBase(ABC):
    @abstractmethod
    def exec(self, sql, args=None):
        pass

    @abstractmethod
    def transaction(self, operation):
        pass


class Pgsql(PgsqlBase):
    def __init__(self, min_con, max_con, *args, **kwargs):
        self._pool = ThreadedConnectionPool(
            min_con, max_con, *args, connection_factory=NamedTupleConnection, **kwargs
        )

    def exec(self, sql, args=None):
        def t(conn):
            with conn.cursor() as c:
                c.execute(sql, args)
                try:
                    res = c.fetchall()
                    return res
                except ProgrammingError:
                    pass

        r = self.transaction(t)
        return r

    def transaction(self, operation):
        conn = self._pool.getconn()
        try:
            with conn:
                return operation(conn)
        finally:
            self._pool.putconn(conn)
