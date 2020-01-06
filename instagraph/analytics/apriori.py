from efficient_apriori import apriori

from instagraph.persistence.interfaces import User, Users
from instagraph.persistence.pg.pgsql import PgsqlBase


class Apriori:
    def __init__(self, most_popular_users: "MostPopularSubscriptions", min_support, min_confidence):
        self._min_sup = min_support
        self._min_conf = min_confidence
        self._most_popular_users = most_popular_users

    def result(self):
        apriori(
            self._most_popular_users.subscriptions_lists(),
            min_support=0.1,
            min_confidence=0.3
        )


class MostPopularSubscriptions:
    def __init__(self, pgsql: PgsqlBase, users: Users, audience_of: User):
        self._target = audience_of
        self._pgsql = pgsql
        self._users = users

    def subscriptions_lists(self):
        subscriptions = {}
        for record in self._pgsql.exec(
            """
            select follower, followed from social.connections
            where followed in
            (
                select followed
                from social.connections 
                inner join (select follower from social.connections where followed = 290866744) as target_followers
                on social.connections.follower = target_followers.follower
                GROUP BY followed
                ORDER BY COUNT(*) DESC
                LIMIT 100
            )
            """
        ):
            if record.follower in subscriptions:
                subscriptions[record.follower].append(record.followed)
            else:
                subscriptions[record.follower] = [record.followed]
        return list(map(tuple, subscriptions.values()))
