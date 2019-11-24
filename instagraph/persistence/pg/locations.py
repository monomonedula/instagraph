from instagraph.persistence.interfaces import Locations
from instagraph.persistence.pg.location import PgLocation


class PgLocations(Locations):
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def location(self, pk):
        self._pgsql.exec(
            "INSERT INTO locations (id) VALUES %s "
            "ON CONFLICT DO NOTHING",
            [pk]
        )
        return PgLocation(self._pgsql, pk)