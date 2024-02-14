from typing import Any, List


class _ArrayType(list):
    pass


class Arrays:
    @classmethod
    def contains(cls, array: _ArrayType, val: str) -> bool:
        """Tests if a value exists in an expression's array."""
        return val in array

    @classmethod
    def add(cls, array: _ArrayType, val: Any) -> _ArrayType:
        """Appends an element to a list and returns the list."""
        return _ArrayType(array + [val])

    @classmethod
    def remove(cls, array: _ArrayType, val: Any) -> _ArrayType:
        """Removes all occurances of a value from a list."""
        return _ArrayType([x for x in array if x != val])

    @classmethod
    def clear(cls, _: _ArrayType) -> _ArrayType:
        """Returns and empty list."""
        return _ArrayType([])

    @classmethod
    def get(cls, array: _ArrayType, index: int) -> Any:
        """Returns element at `index`. If `index` does not exist then returns None."""
        try:
            return array[index]
        except IndexError:
            return None

    @classmethod
    def flatten(cls, *args: _ArrayType) -> _ArrayType:
        """Returns a flattened list from all args."""
        return _ArrayType(
            [item for row in args for item in (row if isinstance(row, list) else [row])]
        )

    @classmethod
    def size(cls, array: _ArrayType) -> int:
        """Returns the number of elements in array."""
        return len(array)

    @classmethod
    def isEmpty(cls, array: _ArrayType) -> bool:
        """Returns if an array is empty or not."""
        return not array

    @classmethod
    def toCsvString(cls, array: _ArrayType) -> str:
        """Returns a comma delineated string from array elements."""
        return ",".join(array)
