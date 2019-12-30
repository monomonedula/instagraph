import argparse
import os

from instagraph.persistence.pg.pgsql import Pgsql


def main(dbname, user, password, host):
    p = Pgsql(
        0,
        10,
        database=dbname,
        user=user,
        password=password,
        host=host,
    )
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "db_setup.sql"
    )
    with open(path) as f:
        script = f.read()
    p.exec(script)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Setup database tables')
    parser.add_argument('--dbname', type=str,
                        help='Postgres db name')
    parser.add_argument('--dbuser', type=str,
                        help='Postgres db user')
    parser.add_argument('--dbpassword', type=str,
                        help='Postgres db password')
    parser.add_argument('--dbhost', type=str,
                        help='Postgres db host', default='localhost')

    args = parser.parse_args()
    main(args.dbname, args.dbuser, args.dbpassword, args.dbhost)
