import json
import os

import pytest

from instagraph.persistence.pg.pgsql import Pgsql


@pytest.fixture()
def pgsql():
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "db_setup.sql"
    )
    config = json.loads(
        open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "secrets-test.json"
            )
        ).read()
    )
    p = Pgsql(
        0,
        10,
        database=config["database"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
    )

    with open(path) as f:
        script = f.read()
    p.exec(script)

    yield Pgsql(
        0,
        10,
        database=config["database"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
        options="-c search_path=social",
    )
    p.exec("DROP SCHEMA IF EXISTS social CASCADE;")
