from abc_delegation import delegation_metaclass

from instagraph.gathering.interfaces import InstaUser


class RecursiveInstaUser(InstaUser, metaclass=delegation_metaclass("_target")):
    def __init__(
        self,
        user: InstaUser,
    ):
        self._target = user

    def save_followers(self):
        print(f"recursive save followers of {self.id()}")
        self._target.save_followers()
        followers = self._target.retrieve_followers()
        for i, f in enumerate(followers, 1):
            print(f"inner recursive save followers of {f.id()}. #{i} of {len(followers)}")
            f.save_followers()

    def save_following(self):
        print(f"recursive save following of {self.id()}")
        self._target.save_following()
        followers = self._target.retrieve_followers()
        for i, f in enumerate(followers, 1):
            print(f"inner recursive save following of {f.id()}. #{i} of {len(followers)}")
            f.save_following()

    def save_info(self):
        print(f"recursive save info of {self.id()}")
        self._target.save_info()
        self._target.save_followers()
        for f in self._target.retrieve_followers():
            print(f"inner recursive save info of {f.id()}")
            f.save_info()

    def save_posts_info(self):
        print(f"recursive save posts info of {self.id()}")
        self._target.save_posts_info()
        print(f"retreive followrs result {self._target.retrieve_followers()}")
        for f in self._target.retrieve_followers():
            print(f"inner recursive posts info of {f.id()}")
            f.save_posts_info()
