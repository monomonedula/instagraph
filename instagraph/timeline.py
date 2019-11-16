from typing import Iterable

from ext.pgsql import Pgsql
from ext.users import Users, User, PgUser, AlreadyFollowing, Followers, Following, UserInfo


class TimelinePgUsers(Users):
    def __init__(self, users, pgsql):
        self._users = users
        self._pgsql = pgsql

    def user(self, user_id):
        return TimelinePgUser(self._users.user(user_id), self._pgsql)


class TimelinePgUser(User):
    def __init__(self, user: PgUser, pgsql: Pgsql):
        self._user = user
        self._pgsql = pgsql

    def id(self):
        return self._user.id()

    def following(self):
        return TimelineFollowing(self._user.following(), self._pgsql)

    def followers(self):
        return TimelineFollowers(self._user.followers(), self._pgsql)

    def schedule_follow(self, user, tags=tuple(), priority=5):
        if self._pgsql.exec(
            "SELECT * FROM connections_timeline "
            "WHERE follower = %s AND "
            "followed = %s",
            (self.id(), user.id()),
        ):
            raise AlreadyFollowing(f"Already following user {user.id()}")
        self._user.schedule_follow(user, tags, priority)

    def info(self) -> "UserInfo":
        return self._user.info()


class TimelineFollowers(Followers):
    def __init__(self, followers: Followers, pgsql):
        self._f = followers
        self._pgsql = pgsql

    def user_id(self):
        return self._f.user_id()

    def number(self):
        return self._f.number()

    def users(self):
        return self._f.users()

    def update_followers(self, users: Iterable[User]):
        users = list(users)
        self._f.update_followers(users)
        new = set(map(lambda u: u.id(), users))
        old = set(
            map(
                lambda r: r.follower,
                self._pgsql.exec(
                    "SELECT follower FROM connections_timeline "
                    "WHERE followed = %s AND ended is NULL",
                    (self.user_id(),),
                ),
            )
        )
        for i in new.difference(old):
            self._pgsql.exec(
                "INSERT INTO connections_timeline (follower, followed, observed) "
                "VALUES (%s, %s, NOW()::date)",
                (i, self.user_id()),
            )
        for i in old.difference(new):
            self._pgsql.exec(
                "UPDATE connections_timeline SET ended = now()::date WHERE "
                "follower = %s AND followed = %s",
                (i, self.user_id()),
            )


class TimelineFollowing(Following):
    def __init__(self, following: Following, pgsql):
        self._f = following
        self._pgsql = pgsql

    def user_id(self):
        return self._f.user_id()

    def number(self):
        return self._f.number()

    def users(self):
        return self._f.users()

    def follow(self, user):
        self._f.follow(user)
        if not self._pgsql.exec(
            "SELECT * FROM connections_timeline "
            "WHERE follower = %s AND followed = %s AND ended is NULL",
            (self.user_id(), user.id()),
        ):
            self._pgsql.exec(
                "INSERT INTO connections_timeline (follower, followed, observed) "
                "VALUES (%s, %s, NOW()::date)",
                (self.user_id(), user.id()),
            )

    def unfollow(self, user):
        self._f.unfollow(user)
        self._pgsql.exec(
            "UPDATE connections_timeline SET ended = now()::date "
            "WHERE follower = %s AND followed = %s AND ended is NULL",
            (self.user_id(), user.id()),
        )

    def update_following(self, users: Iterable[User]):
        users = list(users)
        self._f.update_following(users)
        new = set(map(lambda u: u.id(), users))
        old = set(
            map(
                lambda r: r.followed,
                self._pgsql.exec(
                    "SELECT followed FROM connections_timeline "
                    "WHERE follower = %s AND ended is NULL",
                    (self.user_id(),),
                ),
            )
        )
        for followed in new.difference(old):
            self._pgsql.exec(
                "INSERT INTO connections_timeline (follower, followed, observed) "
                "VALUES (%s, %s, NOW()::date)",
                (self.user_id(), followed),
            )
        for followed in old.difference(new):
            self._pgsql.exec(
                "UPDATE connections_timeline SET ended = now()::date WHERE "
                "followed = %s AND follower = %s",
                (followed, self.user_id()),
            )

    def is_following(self, user):
        return self._f.is_following(user)
