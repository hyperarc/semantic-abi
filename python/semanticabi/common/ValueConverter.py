class ValueConverter:
    """
    Conversion utilities
    """

    @staticmethod
    def hex_to_int(value: str | int) -> int:
        """
        Convert a hex string to an integer
        """
        if isinstance(value, str):
            return int(value, 16)
        else:
            return value
