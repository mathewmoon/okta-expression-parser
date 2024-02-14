from .arrays import _ArrayType


class Groups:
    group_data = {}

    @classmethod
    def getFilteredGroups(
        cls, allow_list: _ArrayType, group_expression: str, limit: int = 5
    ) -> _ArrayType:
        """
        Returns all groups that are in `allow_list`, which is a list of ID's AND the user is a member of. The return value is
        the key specified by `group_expression`. For example, if `group_expression` is "user.name" then
        a list of group names will be returned.
        """
        group_key = group_expression.split(".")[-1]
        res = [cls.group_data.get(x, {}).get(group_key) for x in allow_list]

        if not res:
            return _ArrayType(res)

        if len(res) > limit:
            res = res[0:limit]

        return _ArrayType([x for x in res if x is not None])
