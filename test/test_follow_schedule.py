import pytest

from instagraph.persistence.interfaces import AlreadyFollowing
from instagraph.persistence.pg.schedule import PgFollowSchedule
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
    attempts to schedule follow for the same two users will succeed
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
