from datetime import datetime

from instagraph.gathering.interfaces import InstaPost
from instagraph.persistence.interfaces import Post, Users, Locations


class SimpleInstaPost(InstaPost):
    def __init__(self, bot, post: Post, users: Users, locations: Locations, info, media_id):
        self._bot = bot
        self._users = users
        self._locations = locations
        self._post = post
        self._info = info
        self._media_id = media_id

    def _location(self):
        location = self._locations.location(self._info["location"]["pk"])
        if "lat" in self._info["location"] and "lng" in self._info["location"]:
            location.update_lat_lng(self._info["location"]["lat"], self._info["location"]["lng"])
        location.update_name(self._info["location"]["name"])
        return location

    def post(self):
        return self._post

    def update_location(self):
        self._post.update_location(self._location())

    def update_caption(self):
        self._post.update_caption(self._info["caption"]["text"])

    def update_taken_at(self):
        self._post.update_taken_at(datetime.fromtimestamp(self._info["taken_at"]))

    def update_likes(self):
        self._post.update_like_count(self._info["like_count"])
        self._post.update_likers(
            [self._users.user(int(_id)) for _id in self._bot.get_media_likers(self._media_id)]
        )

    def update_user_tags(self):
        if "usertags" in self._info:
            self._post.update_user_tags(
                [self._users.user(tag["user"]["pk"]) for tag in self._info["usertags"]["in"]]
            )