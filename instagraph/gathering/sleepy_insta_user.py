from time import sleep

from instagraph.gathering.interfaces import InstaUser


class SleepyInstaUser(InstaUser):
    def __init__(self, sleep_seconds, user: InstaUser):
        self._origin = user
        self._sleep_seconds = sleep_seconds

    def id(self) -> int:
        return self._origin.id()

    def save_followers(self):
        print(f"sleeping save followers of {self.id()}  time: {self._sleep_seconds}")
        sleep(self._sleep_seconds)
        return self._origin.save_followers()

    def save_following(self):
        print(f"sleeping save following of {self.id()}  time: {self._sleep_seconds}")
        sleep(self._sleep_seconds)
        return self._origin.save_following()

    def save_info(self):
        print(f"sleeping save info of {self.id()}  time: {self._sleep_seconds}")
        sleep(self._sleep_seconds)
        return self._origin.save_info()

    def save_posts_info(self):
        print(f"sleeping save posts info of {self.id()}  time: {self._sleep_seconds}")
        sleep(self._sleep_seconds)
        return self._origin.save_posts_info()

    def retrieve_followers(self):
        print(f"sleeping retrieve followers info of {self.id()} {self} time: {self._sleep_seconds}")
        sleep(self._sleep_seconds)
        return self._origin.retrieve_followers()

    def retrieve_following(self):
        print(f"sleeping retrieve following info of {self.id()} {self}  time: {self._sleep_seconds}")
        sleep(self._sleep_seconds)
        return self._origin.retrieve_following()
