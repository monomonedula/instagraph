from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple, Iterable


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


class Actions:
    @abstractmethod
    def followers_explored(self, user_id):
        pass

    @abstractmethod
    def following_explored(self, user_id):
        pass

    @abstractmethod
    def info_saved(self, user_id):
        pass

    @abstractmethod
    def media_info_saved(self, user_id):
        pass

    @abstractmethod
    def mark_followers_explored(self, user_id):
        pass

    @abstractmethod
    def mark_following_explored(self, user_id):
        pass

    @abstractmethod
    def mark_info_saved(self, user_id):
        pass

    @abstractmethod
    def mark_posts_info_saved(self, user_id):
        pass

    @abstractmethod
    def posts_info_saved(self, user_id):
        pass


class FollowSchedule(ABC):
    @abstractmethod
    def users_to_be_followed(self, by: User) -> Iterable[User]:
        pass

    @abstractmethod
    def mark_fulfilled(self, follower: User, followed: User):
        pass

    @abstractmethod
    def mark_rejected(self, follower: User, followed: User, reason=None):
        pass


class AlreadyFollowing(Exception):
    pass
