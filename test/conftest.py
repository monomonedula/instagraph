import os

import pytest

from instagraph.pgsql import Pgsql


@pytest.fixture()
def pgsql():
    p = Pgsql(0, 10, database="test", user="test", password="test", host="localhost",)
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "db_setup.sql"
    )
    with open(path) as f:
        script = f.read()
    p.exec(script)

    yield Pgsql(
        0,
        10,
        database="test",
        user="test",
        password="test",
        host="localhost",
        options="-c search_path=social",
    )
    p.exec("DROP SCHEMA IF EXISTS social CASCADE;")
