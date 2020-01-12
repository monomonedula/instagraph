from instagraph.gathering.interfaces import InstaUser


class Scan:
    def __init__(self, target_user: "InstaUser"):
        self._target = target_user

    def run(self):
        self._target.save_info()
        print(f"scan saving followers of {self._target.id()}")
        self._target.save_followers()
        print(f"scan saving following of {self._target.id()}")
        self._target.save_following()
        # print(f"scan saving followers of {self._target.id()}")
        # self._target.save_followers()
        print(f"scan saving posts info of {self._target.id()}")
        self._target.save_posts_info()
