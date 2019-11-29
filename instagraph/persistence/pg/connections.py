from typing import Iterable

from instagraph.persistence.interfaces import Following, Followers, User, Users


class PgUserFollowing(Following):
    def __init__(self, pgsql, user_id, users: Users):
        self._uid = user_id
        self._pgsql = pgsql
        self._users = users

    def user_id(self):
        return self._uid

    def number(self):
        return self._pgsql.exec(
            "SELECT nfollows FROM users WHERE id = %s", (self._uid,)
        )[0][0]

    def users(self):
        return map(
            lambda record: self._users.user(record[0]),
            self._pgsql.exec(
                "SELECT followed FROM connections WHERE follower = %s ", (self._uid,)
            ),
        )

    def follow(self, user):
        self._pgsql.exec(
            "INSERT INTO connections (follower, followed) VALUES (%s, %s) "
            "ON CONFLICT DO NOTHING",
            (self.user_id(), user.id()),
        )

    def unfollow(self, user):
        self._pgsql.exec(
            "DELETE FROM connections WHERE follower = %s AND followed = %s",
            (self.user_id(), user.id()),
        )

    def update_following(self, following):
        new = {f.id() for f in following}
        old = {
            row.followed
            for row in self._pgsql.exec(
                "SELECT followed FROM connections WHERE follower = %s",
                (self.user_id(),),
            )
        }
        for i in new.difference(old):
            self._pgsql.exec(
                "INSERT INTO connections (follower, followed) VALUES (%s, %s)"
                " ON CONFLICT DO NOTHING",
                (self.user_id(), i),
            )
        for i in old.difference(new):
            self._pgsql.exec(
                "DELETE FROM connections WHERE follower = %s AND followed = %s",
                (self.user_id(), i),
            )

    def is_following(self, user):
        return bool(
            self._pgsql.exec(
                "SELECT * FROM connections WHERE follower = %s AND followed = %s",
                (self.user_id(), user.id()),
            )
        )


class PgUserFollowers(Followers):
    def __init__(self, pgsql, user_id, users: Users):
        self._uid = user_id
        self._pgsql = pgsql
        self._users = users

    def user_id(self):
        return self._uid

    def number(self):
        return self._pgsql.exec(
            "SELECT nfollowers FROM users WHERE id = %s", (self._uid,)
        )[0][0]

    def users(self):
        return map(
            lambda record: self._users.user(record[0]),
            self._pgsql.exec(
                "SELECT follower FROM connections WHERE followed = %s ", (self._uid,)
            ),
        )

    def update_followers(self, followers: Iterable[User]):
        new = {f.id() for f in followers}
        old = {
            row.follower
            for row in self._pgsql.exec(
                "SELECT follower FROM connections WHERE followed = %s",
                (self.user_id(),),
            )
        }
        for i in new.difference(old):
            self._pgsql.exec(
                "INSERT INTO connections (follower, followed) VALUES (%s, %s)"
                " ON CONFLICT DO NOTHING",
                (i, self.user_id()),
            )
        for i in old.difference(new):
            self._pgsql.exec(
                "DELETE FROM connections WHERE follower = %s AND followed = %s",
                (i, self.user_id()),
            )