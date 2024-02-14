class Convert:
    @classmethod
    def toInt(val: str | float) -> int:
        """Casts a string to an int."""
        try:
            return int(val)
        except ValueError:
            return 0

    @classmethod
    def toNum(val: str) -> float:
        try:
            return float(val)
        except ValueError:
            return 0
