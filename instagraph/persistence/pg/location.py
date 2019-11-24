from typing import Tuple

from instagraph.persistence.interfaces import Location


class PgLocation(Location):
    def __init__(self, pgsql, location_id):
        self._pgsql = pgsql
        self._id = location_id

    def id(self):
        return self._id

    def update_lat_lng(self, lat: float, lng: float) -> None:
        self._pgsql.exec(
            "UPDATE locations SET lat = %s, lng = %s WHERE id = %s",
            [lat, lng, self._id]
        )

    def update_name(self, name: str) -> None:
        self._pgsql.exec(
            "UPDATE locations SET name = %s WHERE id = %s",
            [name, self._id]
        )

    def name(self) -> str:
        return self._pgsql.exec(
            "SELECT name FROM locations WHERE id = %s",
            [self._id]
        )[0].name

    def lat_lng(self) -> Tuple[float, float]:
        return self._pgsql.exec(
            "SELECT lat, lng FROM locations WHERE id = %s",
            [self._id]
        )[0]