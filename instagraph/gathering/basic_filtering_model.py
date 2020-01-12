

class BasicFilteringModel:
    _commercial_categories = {
        "Local Business",
        "Product/Service",
        "Education",
        "Health/Beauty",
        "Brand",
        "Sports & Recreation",
        "Cafe",
        "Tattoo & Piercing Shop",
        "Food & Beverage",
        "Restaurant",
        "Internet Company",
        "Pet Supplies",
        "Elementary School",
        "Charity Organization",
        "Clothing (Brand)",
        "Travel Company",
        "Shopping Service",
        "Nonprofit Organization",
        "Home Decor",
        "Retail Company",
        "Lingerie & Underwear Store",
        "Business"
    }

    def __init__(self, commerical_categories=None):
        if commerical_categories is not None:
            self._commercial_categories = commerical_categories

    def is_target(self, info: dict):
        tags = self.tags(info)
        return not ("massfollower" in tags or "commerce" in tags)

    def tags(self, info: dict):
        tags = self._category_check(info.get("category") or "")
        followers_count = info["follower_count"]
        following_count = info["following_count"]
        if (following_count > 1000 and followers_count < 10000) or following_count > 1500:
            tags.append("massfollower")
        return tags

    def _category_check(self, category):
        if category in self._commercial_categories or (
            "store" in category.lower()
            or
            "business" in category.lower()
            or
            "shop" in category.lower()
            or
            "brand" in category.lower()
        ):
            return ["commerce"]
        return []
