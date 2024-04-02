from enum import Enum


class ItemType(Enum):
    """
    The different possible values for the `type` field in an ABI item.

    @author garrett
    """

    EVENT = "event"
    FUNCTION = "function"
    CONSTRUCTOR = "constructor"
    FALLBACK = "fallback"
    RECEIVE = "receive"
    ERROR = "error"

    @staticmethod
    def is_function_type(item_type: 'ItemType') -> bool:
        """
        Returns true if the item type is a function type.
        """
        return item_type in [ItemType.FUNCTION, ItemType.CONSTRUCTOR, ItemType.FALLBACK, ItemType.RECEIVE]