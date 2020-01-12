import pytest

from instagraph.persistence.pg.users import PgUsers


@pytest.mark.postgresql
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
    user.info().add_tag("kids")


@pytest.mark.postgresql
def test_followers(pgsql):
    users = PgUsers(pgsql)
    user = users.user(12345)
    user.followers().update_followers(
        [users.user(i) for i in range(400)]
    )
    assert {u.id() for u in user.followers().users()} == set(range(400))
    user.followers().update_followers(
        [users.user(i) for i in range(20, 440)]
    )
    assert {u.id() for u in user.followers().users()} == set(range(20, 440))


@pytest.mark.postgresql
def test_following(pgsql):
    users = PgUsers(pgsql)
    user = users.user(12345)
    user.following().update_following(
        [users.user(i) for i in range(400)]
    )
    assert {u.id() for u in user.following().users()} == set(range(400))
    user.following().update_following(
        [users.user(i) for i in range(20, 440)]
    )
    assert {u.id() for u in user.following().users()} == set(range(20, 440))


@pytest.mark.postgresql
def test_following_follow_unfollow(pgsql):
    users = PgUsers(pgsql)
    user = users.user(12345)
    user.following().follow(users.user(11111))
    assert [u.id() for u in user.following().users()] == [11111]
    user.following().unfollow(users.user(11111))
    assert [u.id() for u in user.following().users()] == []
