from abc import ABC, abstractmethod
from typing import Iterable


class InstaUser(ABC):
    @abstractmethod
    def id(self) -> int:
        pass

    @abstractmethod
    def save_followers(self):
        pass

    @abstractmethod
    def save_following(self):
        pass

    @abstractmethod
    def save_info(self):
        pass

    @abstractmethod
    def save_posts_info(self):
        pass

    @abstractmethod
    def retrieve_followers(self):
        pass

    @abstractmethod
    def retrieve_following(self):
        pass


class InstaPost(ABC):
    @abstractmethod
    def post(self):
        pass

    @abstractmethod
    def update_location(self):
        pass

    @abstractmethod
    def update_caption(self):
        pass

    @abstractmethod
    def update_taken_at(self):
        pass

    @abstractmethod
    def update_likes(self):
        pass

    @abstractmethod
    def update_user_tags(self):
        pass


class InstaUserPosts(ABC):
    def posts(self) -> Iterable[InstaPost]:
        pass
