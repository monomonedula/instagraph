from instagraph.gathering.interfaces import InstaUser


class Scan:
    def __init__(self, target_user: "InstaUser"):
        self._target = target_user

    def run(self):
        self._target.save_info()
        self._target.save_followers()
        self._target.save_following()
        self._target.save_posts_info()
