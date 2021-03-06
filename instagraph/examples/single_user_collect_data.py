import argparse
from datetime import timedelta

from instabot import Bot

from instagraph.gathering.basic_filtering_model import BasicFilteringModel
from instagraph.gathering.interfaces import InstaUser, InstaUserPosts
from instagraph.gathering.lazy_insta_user import LazyInstaUser, CachedLazyUser
from instagraph.gathering.noncommercial_insta_user import NonCommercialInstaUser
from instagraph.gathering.recursive_insta_user import RecursiveInstaUser
from instagraph.gathering.scan import Scan
from instagraph.gathering.simple_insta_user import SimpleInstaUser
from instagraph.gathering.simple_posts import SimpleInstaUserPosts
from instagraph.gathering.sleepy_insta_user import SleepyInstaUser
from instagraph.gathering.smart_insta_user import SmartInstaUser
from instagraph.persistence.interfaces import User
from instagraph.persistence.pg.actions import PgActions, PgActionsWithExpiration
from instagraph.persistence.pg.locations import PgLocations
from instagraph.persistence.pg.pgsql import Pgsql
from instagraph.persistence.pg.users import PgUsers


def main(pgsql, bot, user_id):
    def user_factory(id_: int) -> InstaUser:
        return user_to_insta_user(PgUsers(pgsql).user(id_))

    def user_to_insta_user(user: User):
        return NonCommercialInstaUser(
            pgsql,
            LazyInstaUser(
                insta_user=SmartInstaUser(
                    bot=bot,
                    model=BasicFilteringModel(),
                    insta_user=SleepyInstaUser(
                        30,
                        SimpleInstaUser(bot, user, user_factory, posts_factory)
                    ),
                    user=user,
                    pgsql=pgsql
                ),
                actions=PgActions(pgsql),
                db_user=user,
            ),
        )

    def posts_factory(user: User) -> InstaUserPosts:
        return SimpleInstaUserPosts(bot, user, PgUsers(pgsql), PgLocations(pgsql))

    Scan(
        RecursiveInstaUser(
            CachedLazyUser(
                insta_user=SleepyInstaUser(
                    30,
                    SimpleInstaUser(
                        bot,
                        PgUsers(pgsql).user(user_id),
                        user_factory,
                        posts_factory
                    ),
                ),
                actions=PgActionsWithExpiration(pgsql, timedelta(days=10)),
                db_user=PgUsers(pgsql).user(user_id),
                make_insta_user=user_to_insta_user
            ),
        )
    ).run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save data of a user")
    parser.add_argument("--id", type=int, help="User's id")
    parser.add_argument("--insta_login", type=str, help="Instagram username")
    parser.add_argument("--insta_password", type=str, help="Instagram username")
    parser.add_argument("--dbname", type=str, help="Postgres db name")
    parser.add_argument("--dbuser", type=str, help="Postgres db user")
    parser.add_argument("--dbpassword", type=str, help="Postgres db password")
    parser.add_argument(
        "--dbhost", type=str, help="Postgres db host", default="localhost"
    )

    args = parser.parse_args()

    bot = Bot()
    bot.login(username=args.insta_login, password=args.insta_password)
    main(
        Pgsql(
            0,
            10,
            database=args.dbname,
            user=args.dbuser,
            password=args.dbpassword,
            host=args.dbhost,
            options="-c search_path=social",
        ),
        bot,
        args.id,
    )
