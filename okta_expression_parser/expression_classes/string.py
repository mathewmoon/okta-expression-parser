from typing import Tuple


class String:
    @classmethod
    def stringContains(cls, str_to_test: str, val: str):
        """Tests if a string contains another string"""
        res = (
            isinstance(str_to_test, str) and isinstance(val, str) and val in str_to_test
        )
        return res

    @classmethod
    def startsWith(self, str_to_test: str, val: str):
        """Tests if a string starts with another string"""
        return (
            isinstance(str_to_test, str)
            and isinstance(val, str)
            and str_to_test.startswith(val)
        )

    @classmethod
    def toLowerCase(self, val: str):
        """Casts to lower case"""
        if isinstance(val, str):
            return val.lower()

        return val

    @classmethod
    def toUpperCase(self, val: str):
        """Casts to upper case"""
        if isinstance(val, str):
            return val.upper()
        return val

    @classmethod
    def append(self, val1: str, val2: str):
        """Concatenates two strings"""
        return f"{val1}${val2}"

    @classmethod
    def join(self, separator: str, *vals: Tuple[str]):
        """Returns a joined string using separator"""
        return separator.join(list(vals))

    @classmethod
    def removeSpaces(self, val: str):
        """Removes spaces from a string"""
        return str(val).replace(" ", "")

    @classmethod
    def replace(self, val: str, match: str, replacement: str):
        """Replace all occurances of match with replacement in val"""
        return str(val).replace(match, replacement)

    @classmethod
    def replaceFirst(self, val: str, match: str, replacement: str):
        """Replace first occurance of match with replacement in val"""
        return str(val).replace(match, replacement, 1)

    @classmethod
    def startsWith(self, val: str, test: str):
        """Returns whether val starts with test"""
        return str(val).startswith(test)

    @classmethod
    def contains(self, val: str, test: str):
        """Return whether val contains test"""
        return str(test) in str(val)

    @classmethod
    def stringSwitch(self, val: str, default: str, *kv_pairs: Tuple[str]):
        """Set defaultss"""
        if len(kv_pairs) % 2 != 0:
            return False

        kv_pairs = list(kv_pairs)

        while kv_pairs:
            k = kv_pairs.pop(0)
            v = kv_pairs.pop(0)

            if k in val:
                return v

        return default

    @classmethod
    def substring(self, val: str, start: int, end: int):
        """Return a substring of val starting at index start"""
        if not isinstance(val, str):
            return ""

        if end > len(val):
            end = -1

        return val[int(start) : int(end)]

    @classmethod
    def substringAfter(self, val: str, search: str):
        try:
            start = str(val).index(str(search))
        except ValueError:
            return val

        return val[start:]

    @classmethod
    def substringBefore(self, val: str, search: str):
        """Return substring of val starting after the index of search string"""
        try:
            end = str(val).index(str(search))
        except ValueError:
            return val

        return val[0:end]
