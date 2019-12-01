from instagraph.persistence.interfaces import UserInfo
from instagraph.persistence.pg.pgsql import PgsqlBase


class PgUserInfo(UserInfo):
    def __init__(self, pgsql: PgsqlBase, user_id):
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