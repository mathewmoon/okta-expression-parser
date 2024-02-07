from typing import Any, List


class Arrays:
    @classmethod
    def contains(cls, array: List[Any], val: str):
        """Tests if a value exists in an expression's array"""
        return val in array
