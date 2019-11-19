from networkx import DiGraph

from instagraph.persistence.users import PgUser


class Graph:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def edges(self):
        self._pgsql.exec(
            "SELECT follower, followed FROM connections "
            "WHERE follower NOT IN mass_followers AND followed NOT IN mass_followers "
            "WHERE (SELECT id FROM users WHERE nfollows > 500)"
        )

    def user(self, user_id):
        return PgUser(self._pgsql, user_id)


def networkx_from_db(pgsql):
    dg = DiGraph()
    dg.add_edges_from(
        pgsql.exec(
            "WITH mass_followers AS (SELECT id FROM users WHERE nfollows > 500) "
            "SELECT follower, followed FROM connections "
            "WHERE follower NOT IN (SELECT id FROM mass_followers)"
            " AND followed NOT IN (SELECT id FROM mass_followers) "
        )
    )
    return dg
