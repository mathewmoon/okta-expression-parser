class String:
    @classmethod
    def stringContains(cls, str_to_test: str, val: str):
        """Tests if a string contains another string"""
        return (
            isinstance(str_to_test, str) and isinstance(val, str) and val in str_to_test
        )

    @classmethod
    def startsWith(self, str_to_test: str, val: str):
        """Tests if a string starts with another string"""
        return (
            isinstance(str_to_test, str)
            and isinstance(val, str)
            and str_to_test.startswith(val)
        )
