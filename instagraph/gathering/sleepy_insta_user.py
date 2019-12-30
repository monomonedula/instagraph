from time import sleep

from instagraph.gathering.interfaces import InstaUser


class SleepyInstaUser(InstaUser):
    def __init__(self, sleep_seconds, user: InstaUser):
        self._origin = user
        self._sleep_seconds = sleep_seconds

    def id(self) -> int:
        return self._origin.id()

    def save_followers(self):
        sleep(self._sleep_seconds)
        return self.save_followers()

    def save_following(self):
        sleep(self._sleep_seconds)
        return self.save_following()

    def save_info(self):
        sleep(self._sleep_seconds)
        return self.save_info()

    def save_posts_info(self):
        sleep(self._sleep_seconds)
        return self.save_posts_info()

    def retrieve_followers(self):
        sleep(self._sleep_seconds)
        return self.retrieve_followers()

    def retrieve_following(self):
        sleep(self._sleep_seconds)
        return self.retrieve_following()
