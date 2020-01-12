from instagraph.gathering.interfaces import InstaUserPosts
from instagraph.gathering.simple_post import SimpleInstaPost
from instagraph.persistence.interfaces import User, Users, Locations


class SimpleInstaUserPosts(InstaUserPosts):
    def __init__(self, bot, user: User, users: Users, locations: Locations):
        self._bot = bot
        self._user = user
        self._users = users
        self._locations = locations

    def posts(self):
        for m_id in self._bot.get_last_user_medias(self._user.id(), 6):
            info = self._bot.get_media_info(m_id)[0]
            yield SimpleInstaPost(
                self._bot,
                self._user.media().post(info["pk"]),
                self._users,
                self._locations,
                info,
                m_id,
            )


