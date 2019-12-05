import pytest

from instagraph.persistence.pg.actions import PgActions
from instagraph.persistence.pg.users import PgUsers


@pytest.mark.postgresql
def test_actions_followers_explored(pgsql):
    users = PgUsers(pgsql)
    users.user(1234)
    actions = PgActions(pgsql)
    actions.mark_followers_explored(1234)
    assert actions.followers_explored(1234)


@pytest.mark.postgresql
def test_actions_following_explored(pgsql):
    users = PgUsers(pgsql)
    users.user(1234)
    actions = PgActions(pgsql)
    actions.mark_following_explored(1234)
    assert actions.following_explored(1234)


@pytest.mark.postgresql
def test_actions_info_saved(pgsql):
    users = PgUsers(pgsql)
    users.user(1234)
    actions = PgActions(pgsql)
    actions.mark_info_saved(1234)
    assert actions.info_saved(1234)


@pytest.mark.postgresql
def test_actions_posts_info_saved(pgsql):
    users = PgUsers(pgsql)
    users.user(1234)
    actions = PgActions(pgsql)
    actions.mark_posts_info_saved(1234)
    assert actions.posts_info_saved(1234)
