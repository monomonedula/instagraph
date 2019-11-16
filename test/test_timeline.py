from datetime import date

from ext.users import PgUsers
from ext.timeline import TimelinePgUsers


def test_timeline_followers(pgsql):
    users = TimelinePgUsers(PgUsers(pgsql), pgsql)
    user = users.user(12345)
    user.followers().update_followers(
        [users.user(33333), users.user(44444), users.user(55523)]
    )
    assert {u.id() for u in user.followers().users()} == {33333, 44444, 55523}
    user.followers().update_followers(
        [users.user(33333), users.user(55523), users.user(22222)]
    )
    assert {u.id() for u in user.followers().users()} == {33333, 22222, 55523}


def test_timeline_following(pgsql):
    users = TimelinePgUsers(PgUsers(pgsql), pgsql)
    user = users.user(12345)
    user.following().update_following(
        [users.user(33333), users.user(44444), users.user(55523)]
    )
    assert {u.id() for u in user.following().users()} == {33333, 44444, 55523}
    user.following().update_following(
        [users.user(33333), users.user(55523), users.user(22222)]
    )
    assert {u.id() for u in user.following().users()} == {33333, 22222, 55523}
    records = pgsql.exec("SELECT * FROM connections_timeline")
    assert set(records) == {
        (12345, 33333, date.today(), None),
        (12345, 55523, date.today(), None),
        (12345, 44444, date.today(), date.today()),
        (12345, 22222, date.today(), None),
    }


def test_following_follow_unfollow(pgsql):
    users = TimelinePgUsers(PgUsers(pgsql), pgsql)
    user = users.user(12345)
    user.following().follow(users.user(11111))
    assert [u.id() for u in user.following().users()] == [11111]
    user.following().unfollow(users.user(11111))
    assert [u.id() for u in user.following().users()] == []
    records = pgsql.exec("SELECT * FROM connections_timeline")
    assert records == [
        (12345, 11111, date.today(), date.today()),
    ]
