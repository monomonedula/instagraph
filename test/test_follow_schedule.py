import pytest

from instagraph.persistence.interfaces import AlreadyFollowing, AlreadyNotFollowing
from instagraph.persistence.pg.schedule import PgFollowSchedule, PgUnfollowSchedule
from instagraph.persistence.pg.users import PgUsers


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_add_record(pgsql):
    """
    Should add records correctly
    """
    users = PgUsers(pgsql)
    user = users.user(123)
    PgFollowSchedule(pgsql, users).add_record(user, users.user(456))
    PgFollowSchedule(pgsql, users).add_record(user, users.user(436), ("some_tag",), 4)
    to_be_followed = PgFollowSchedule(pgsql, users).users_to_be_followed(user)
    ids = [u.id() for u in to_be_followed]
    assert len(ids) == 2
    assert set(ids) == {456, 436}


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_add_record_already_following(pgsql):
    """
    Should raise AlreadyFollowing error when trying to add record
    for an existing relation
    """
    users = PgUsers(pgsql)
    user = users.user(123)
    user.following().follow(users.user(456))
    with pytest.raises(AlreadyFollowing):
        PgFollowSchedule(pgsql, users).add_record(user, users.user(456))


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_fulfilled(pgsql):
    """
    Should mark records fulfilled
    """
    users = PgUsers(pgsql)
    schedule = PgFollowSchedule(pgsql, users)
    schedule.add_record(users.user(123), users.user(321))
    schedule.mark_fulfilled(users.user(123), users.user(321))
    assert list(schedule.users_to_be_followed(users.user(123))) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_fulfilled_nonexistent(pgsql):
    """
    Does nothing if record to be marked fulfilled is not present
    """
    users = PgUsers(pgsql)
    schedule = PgFollowSchedule(pgsql, users)
    schedule.mark_fulfilled(users.user(123), users.user(321))


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_rejected(pgsql):
    """
    should mark records as rejected
    """
    users = PgUsers(pgsql)
    schedule = PgFollowSchedule(pgsql, users)
    schedule.add_record(users.user(123), users.user(321))
    schedule.mark_rejected(users.user(123), users.user(321))
    assert list(schedule.users_to_be_followed(users.user(123))) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_rejected_nonexistent(pgsql):
    """
    Does nothing if record to be marked rejected is not present
    """
    users = PgUsers(pgsql)
    schedule = PgFollowSchedule(pgsql, users)
    schedule.mark_rejected(users.user(123), users.user(321))


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_rejected_repeat(pgsql):
    """
    If a rejected record for given follow relation is present in db,
    attempts to schedule follow for the same two users will not succeed
    """
    users = PgUsers(pgsql)
    schedule = PgFollowSchedule(pgsql, users)
    schedule.add_record(users.user(123), users.user(555))
    schedule.mark_rejected(users.user(123), users.user(555))
    schedule.add_record(users.user(123), users.user(555))
    assert list(schedule.users_to_be_followed(users.user(123))) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_fulfilled_repeat(pgsql):
    """
    If a fulfilled record for given follow relation is present in db,
    attempts to schedule follow for the same two users will succeed
    """
    users = PgUsers(pgsql)
    schedule = PgFollowSchedule(pgsql, users)
    schedule.add_record(users.user(123), users.user(555))
    schedule.mark_fulfilled(users.user(123), users.user(555))
    schedule.add_record(users.user(123), users.user(555))
    assert list(schedule.users_to_be_followed(users.user(123))) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_mark_fulfilled_add_record(pgsql):
    """
    Should add records correctly
    """
    users = PgUsers(pgsql)
    user1 = users.user(123)
    user1.following().follow(users.user(456))
    user1.following().follow(users.user(436))
    schedule = PgUnfollowSchedule(pgsql, users)
    schedule.add_record(user1, users.user(456))
    schedule.add_record(user1, users.user(436), ("some_tag",), 4)
    to_be_unfollowed = schedule.users_to_be_unfollowed(user1)
    ids = [u.id() for u in to_be_unfollowed]
    assert len(ids) == 2
    assert set(ids) == {456, 436}


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_add_record_already_not_following(pgsql):
    """
    Should raise AlreadyNotFollowing error when trying to add record
    for an already nonexistent relation
    """
    users = PgUsers(pgsql)
    user = users.user(123)
    with pytest.raises(AlreadyNotFollowing):
        PgUnfollowSchedule(pgsql, users).add_record(user, users.user(456))


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_mark_fulfilled(pgsql):
    """
    Should mark records fulfilled
    """
    users = PgUsers(pgsql)
    schedule = PgUnfollowSchedule(pgsql, users)
    user1, user2 = users.user(123), users.user(321)
    user1.following().follow(user2)
    schedule.add_record(user1, user2)
    schedule.mark_fulfilled(user1, user2)
    assert list(schedule.users_to_be_unfollowed(user1)) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_mark_fulfilled_nonexistent(pgsql):
    """
    Does nothing if record to be marked fulfilled is not present
    """
    users = PgUsers(pgsql)
    schedule = PgUnfollowSchedule(pgsql, users)
    schedule.mark_fulfilled(users.user(123), users.user(321))


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_mark_rejected(pgsql):
    """
    should mark records as rejected
    """
    users = PgUsers(pgsql)
    user1, user2 = users.user(123), users.user(321)
    user1.following().follow(user2)
    schedule = PgUnfollowSchedule(pgsql, users)
    schedule.add_record(user1, user2)
    schedule.mark_rejected(user1, user2)
    assert list(schedule.users_to_be_unfollowed(user1)) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_mark_rejected_nonexistent(pgsql):
    """
    Does nothing if record to be marked rejected is not present
    """
    users = PgUsers(pgsql)
    schedule = PgUnfollowSchedule(pgsql, users)
    schedule.mark_rejected(users.user(123), users.user(321))


@pytest.mark.integration
@pytest.mark.postgresql
def test_unfollow_schedule_mark_rejected_repeat(pgsql):
    """
    If a rejected record for given follow relation is present in db,
    attempts to schedule follow for the same two users will not succeed
    """
    users = PgUsers(pgsql)
    schedule = PgUnfollowSchedule(pgsql, users)
    user1, user2 = users.user(123), users.user(555)
    user1.following().follow(user2)
    schedule.add_record(user1, user2)
    schedule.mark_rejected(user1, user2)
    schedule.add_record(user1, user2)
    assert list(schedule.users_to_be_unfollowed(users.user(123))) == []


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_mark_fulfilled_repeat(pgsql):
    """
    If a fulfilled record for given follow relation is present in db,
    attempts to schedule follow for the same two users will succeed
    """
    users = PgUsers(pgsql)
    schedule = PgUnfollowSchedule(pgsql, users)
    user1 = users.user(123)
    user2 = users.user(555)
    user1.following().follow(user2)
    schedule.add_record(user1, user2)
    schedule.mark_fulfilled(user1, user2)
    schedule.add_record(user1, user2)
    assert list(schedule.users_to_be_unfollowed(users.user(123))) == []
