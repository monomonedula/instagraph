import pytest

from instagraph.persistence.interfaces import AlreadyFollowing
from instagraph.persistence.pg.schedule import PgFollowSchedule
from instagraph.persistence.pg.users import PgUsers


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_add_record(pgsql):
    users = PgUsers(pgsql)
    user = users.user(123)
    PgFollowSchedule(pgsql, users).add_record(user, users.user(456))
    PgFollowSchedule(pgsql, users).add_record(user, users.user(436), ("some_tag",), 4)
    to_be_followed = PgFollowSchedule(pgsql, users).users_to_be_followed(user)
    assert set((u.id() for u in to_be_followed)) == {456, 436}


@pytest.mark.integration
@pytest.mark.postgresql
def test_follow_schedule_add_record_already_following(pgsql):
    users = PgUsers(pgsql)
    user = users.user(123)
    user.following().follow(users.user(456))
    with pytest.raises(AlreadyFollowing):
        PgFollowSchedule(pgsql, users).add_record(user, users.user(456))
