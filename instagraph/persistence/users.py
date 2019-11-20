from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Tuple

from .pgsql import Pgsql


class Users(ABC):
    @abstractmethod
    def user(self, user_id) -> "User":
        pass


class User(ABC):
    @abstractmethod
    def id(self) -> int:
        pass

    @abstractmethod
    def following(self) -> "Following":
        pass

    @abstractmethod
    def followers(self) -> "Followers":
        pass

    @abstractmethod
    def schedule_follow(self, user_id, tags=tuple(), priority=5):
        pass

    @abstractmethod
    def info(self) -> "UserInfo":
        pass

    @abstractmethod
    def media(self) -> "UserMedia":
        pass


class Followers(ABC):
    @abstractmethod
    def user_id(self) -> int:
        pass

    @abstractmethod
    def number(self) -> int:
        pass

    @abstractmethod
    def users(self):
        pass

    @abstractmethod
    def update_followers(self, users):
        pass


class Following(ABC):
    @abstractmethod
    def user_id(self) -> int:
        pass

    @abstractmethod
    def number(self) -> int:
        pass

    @abstractmethod
    def users(self):
        pass

    @abstractmethod
    def update_following(self, users):
        pass

    @abstractmethod
    def follow(self, user):
        pass

    @abstractmethod
    def unfollow(self, user):
        pass

    @abstractmethod
    def is_following(self, user) -> bool:
        pass


class UserInfo(ABC):
    @abstractmethod
    def user_id(self) -> int:
        pass

    @abstractmethod
    def update(
        self, *,
        category=None,
        name=None,
        nfollowers=None,
        nfollowing=None,
        nposts=None,
        username=None,
        bio=None,
    ):
        pass

    @abstractmethod
    def add_tag(self, tag):
        pass


class UserMedia(ABC):
    @abstractmethod
    def post(self, post_id, url) -> "Post":
        pass


class Post(ABC):
    @abstractmethod
    def update_caption(self, caption_text: str):
        pass

    @abstractmethod
    def update_location(self, location):
        pass

    @abstractmethod
    def update_like_count(self, count):
        pass

    @abstractmethod
    def update_user_tags(self, users):
        pass

    @abstractmethod
    def update_taken_at(self, dt: datetime):
        pass

    @abstractmethod
    def update_likers(self, users):
        pass


class Locations(ABC):
    @abstractmethod
    def location(self, pk):
        pass


class Location(ABC):
    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def update_lat_lng(self, lat: float, lng: float) -> None:
        pass

    @abstractmethod
    def update_name(self, name: str) -> None:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def lat_lng(self) -> Tuple[float, float]:
        pass


class AlreadyFollowing(Exception):
    pass


class PgUsers(Users):
    def __init__(self, pgsql: Pgsql):
        self._pgsql = pgsql

    def user(
        self, user_id,
    ):
        self._pgsql.exec(
            "INSERT INTO users (id) " "VALUES (%s) ON CONFLICT DO NOTHING", [user_id]
        )
        return PgUser(self._pgsql, user_id)


class FollowSchedule:
    def __init__(self, pgsql):
        self._pgsql = pgsql

    def users_to_be_followed(self, by):
        return map(
            lambda record: PgUser(self._pgsql, record[0]),
            self._pgsql.exec(
                "SELECT user_to_be_followed FROM follow_schedule WHERE user_to_follow = %s "
                " ORDER BY priority ASC",
                (by,),
            ),
        )

    def mark_fulfilled(self, follower, followed):
        self._pgsql.exec(
            "UPDATE follow_schedule SET done = NOW()::date "
            "FROM ( SELECT * FROM follow_schedule"
            "        WHERE follower = %s AND followed = %s ORDER BY scheduled ASC LIMIT 1"
            "      )",
            (follower, followed),
        )
    # TODO: add follow rejection mechanism


class PgUser(User):
    def __init__(self, pgsql, id_):
        self._pgsql = pgsql
        self._id = id_

    def id(self):
        return self._id

    def following(self):
        return PgUserFollowing(self._pgsql, self._id)

    def followers(self):
        return PgUserFollowers(self._pgsql, self._id)

    def schedule_follow(self, user: User, tags=tuple(), priority=5):
        if self.following().is_following(user):
            raise AlreadyFollowing(f"Already following user {user.id()}")
        self._pgsql.exec(
            "INSERT INTO follow_schedule (user_to_follow, user_to_be_followed, scheduled, priority, tags) "
            "VALUES (%s, %s, NOW()::date, %s, %s) ON CONFLICT DO NOTHING",
            (self._id, user.id(), priority, tags),
        )

    def info(self) -> "UserInfo":
        return PgUserInfo(self._pgsql, self.id())

    def media(self) -> "UserMedia":
        return PgUserMedia(self._pgsql, self.id())


class PgUserFollowing(Following):
    def __init__(self, pgsql, user_id):
        self._uid = user_id
        self._pgsql = pgsql

    def user_id(self):
        return self._uid

    def number(self):
        return self._pgsql.exec(
            "SELECT nfollows FROM users WHERE id = %s", (self._uid,)
        )[0][0]

    def users(self):
        return map(
            lambda record: PgUser(self._pgsql, record[0]),
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
    def __init__(self, pgsql, user_id):
        self._uid = user_id
        self._pgsql = pgsql

    def user_id(self):
        return self._uid

    def number(self):
        return self._pgsql.exec(
            "SELECT nfollowers FROM users WHERE id = %s", (self._uid,)
        )[0][0]

    def users(self):
        return map(
            lambda record: PgUser(self._pgsql, record[0]),
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


class PgUserInfo(UserInfo):
    def __init__(self, pgsql: Pgsql, user_id):
        self._pgsql = pgsql
        self._user_id = user_id

    def user_id(self) -> int:
        return self._user_id

    def update(
        self, *,
        category=None,
        name=None,
        nfollowers=None,
        nfollowing=None,
        nposts=None,
        username=None,
        bio=None,
    ):
        name_arg = [
            p
            for p in [
                ("username", username),
                ("name", name),
                ("nfollowers", nfollowers),
                ("nfollows", nfollowing),
                ("posts_number", nposts),
                ("bio", bio),
                ("account_type", category),
            ]
            if p[1] is not None
        ]
        upd = ", ".join(f"{n} = %s" for n in (name for name, _ in name_arg))
        args = [
            i
            for i in (username, name, nfollowers, nfollowing, nposts, bio, category)
            if i is not None
        ]
        self._pgsql.exec(
            f"UPDATE users SET {upd} WHERE id = %s", (*args, self.user_id())
        )

    def add_tag(self, tag):
        self._pgsql.exec(
            "UPDATE users SET tags = array_append(array_remove(tags, %s), %s) "
            "WHERE id = %s",
            (tag, tag, self.user_id()),
        )


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


class PgPost(Post):
    def __init__(self, pgsql: Pgsql, user_id, post_id: int):
        self._pgsql = pgsql
        self._id = post_id
        self._uid = user_id

    def update_caption(self, caption_text: str):
        self._pgsql.exec(
            "UPDATE posts SET caption = %s WHERE user_id = %s AND id = %s",
            (caption_text, self._uid, self._id)
        )

    def update_location(self, location):
        self._pgsql.exec(
            "UPDATE posts SET location = %s WHERE user_id = %s AND id = %s",
            (location.id(), self._uid, self._id)
        )

    def update_like_count(self, count):
        self._pgsql.exec(
            "UPDATE posts SET nlikes = %s WHERE user_id = %s AND id = %s",
            [count, self._uid, self._id]
        )

    def update_user_tags(self, users):
        self._pgsql.exec(
            "UPDATE posts SET user_tags = %s WHERE user_id = %s AND id = %s",
            [[u.id() for u in users], self._uid, self._id]
        )

    def update_taken_at(self, dt: datetime):
        self._pgsql.exec(
            "UPDATE posts SET taken_at = %s WHERE user_id = %s AND id = %s",
            [dt, self._uid, self._id]
        )

    def update_likers(self, users):
        for u in users:
            self._pgsql.exec(
                "INSERT INTO likes (user_id, post_id, post_user_id)"
                " VALUES (%s, %s, %s)"
                " ON CONFLICT DO NOTHING",
                [u.id(), self._id, self._uid]
            )

        self._pgsql.exec(
            "UPDATE posts SET likes = %s WHERE user_id = %s AND id = %s",
            [[u.id() for u in users], self._uid, self._id]
        )


# TODO: implement PgLocations and PgLocation
# TODO: adapt the posts table to the usertags field

