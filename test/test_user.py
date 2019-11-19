from instagraph.persistence.users import PgUsers


def test_user(pgsql):
    user = PgUsers(pgsql).user(12345)
    assert user.id() == 12345
    followers = user.followers()
    assert followers.user_id() == 12345
    assert followers.number() is None
    assert list(followers.users()) == []

    following = user.followers()
    assert following.user_id() == 12345
    assert following.number() is None
    assert list(following.users()) == []
    user.schedule_follow(PgUsers(pgsql).user(123), ["kids"])
    user.info().add_tag("kids")
    pgsql.exec("SELECT * FROM follow_schedule")


def test_followers(pgsql):
    users = PgUsers(pgsql)
    user = users.user(12345)
    user.followers().update_followers(
        [users.user(33333), users.user(44444), users.user(55523)]
    )
    assert {u.id() for u in user.followers().users()} == {33333, 44444, 55523}
    user.followers().update_followers(
        [users.user(33333), users.user(55523), users.user(22222)]
    )
    assert {u.id() for u in user.followers().users()} == {33333, 22222, 55523}


def test_following(pgsql):
    users = PgUsers(pgsql)
    user = users.user(12345)
    user.following().update_following(
        [users.user(33333), users.user(44444), users.user(55523)]
    )
    assert {u.id() for u in user.following().users()} == {33333, 44444, 55523}
    user.following().update_following(
        [users.user(33333), users.user(55523), users.user(22222)]
    )
    assert {u.id() for u in user.following().users()} == {33333, 22222, 55523}


def test_following_follow_unfollow(pgsql):
    users = PgUsers(pgsql)
    user = users.user(12345)
    user.following().follow(users.user(11111))
    assert [u.id() for u in user.following().users()] == [11111]
    user.following().unfollow(users.user(11111))
    assert [u.id() for u in user.following().users()] == []
