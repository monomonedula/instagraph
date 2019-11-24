from instagraph.persistence.interfaces import Users
from instagraph.persistence.pg.timeline.user import TimelinePgUser


class TimelinePgUsers(Users):
    def __init__(self, users, pgsql):
        self._users = users
        self._pgsql = pgsql

    def user(self, user_id):
        return TimelinePgUser(self._users.user(user_id), self._pgsql)