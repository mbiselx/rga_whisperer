"""
This submodule contains all messages whose type code starts with 0x0002.
"""
from dataclasses import dataclass

from .m0000 import Message, MessageParser

__all__ = [
    "BrowseRequestMessage",
    "BrowseResponseMessage",
    "BindRequestMessage",
    "BindResponseMessage",
]


@dataclass
class BrowseRequestMessage(Message, type_code=0x00020200):
    item_name: str
    '''the item being requested for browsing'''
    request_type: int
    '''the type of browse request meing made'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):

        return cls(
            header=header,
            item_name=parser.get_str(),
            request_type=parser.get_int(12),
        )


@dataclass
class BrowseResponseMessage(Message, type_code=0x00020201):

    # i'm so sorry for this...
    @dataclass
    class BrowseItems:
        @dataclass
        class BrowseSubItems:
            short_name: str
            full_name: str
            dtype: int
            item_id: int

            @classmethod
            def parse(cls, parser: MessageParser):
                _ = parser.get_bytes(4)
                dtype = parser.get_int(2)
                _ = parser.get_bytes(2)
                item_id = parser.get_int()
                short_name = parser.get_str()
                if item_id == 5001:  # this seems to be a special type
                    full_name = parser.get_str()
                    _ = parser.get_str()  # this is `Type` again
                else:
                    _ = parser.get_bytes(4)  # null
                    full_name = parser.get_str()
                    # dataType, quality, scanRate all have an extra
                    # empty word appended?
                    if item_id in (1, 3, 6):
                        _ = parser.get_bytes(4)  # null
                return cls(
                    short_name=short_name,
                    full_name=full_name,
                    dtype=dtype,
                    item_id=item_id,
                )

        short_name: str
        full_name: str
        item_type: int
        subitems: list[BrowseSubItems]

        @classmethod
        def parse(cls, parser: MessageParser):
            short_name = parser.get_str()
            full_name = parser.get_str()
            item_type = parser.get_int()
            nb_subitems = parser.get_int(8)

            subitems = [cls.BrowseSubItems.parse(
                parser) for _ in range(nb_subitems)]
            if nb_subitems:
                _ = parser.get_bytes(4)  # null
            return cls(
                short_name=short_name,
                full_name=full_name,
                item_type=item_type,
                subitems=subitems
            )

    items: list[BrowseItems]
    '''list of the items contained in this message'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        _ = parser.get_bytes(12)

        nb_items = parser.get_int()
        items = [cls.BrowseItems.parse(parser) for _ in range(nb_items)]

        return cls(
            header=header,
            items=items,
        )


@dataclass
class BindRequestMessage(Message, type_code=0x00020600):
    channel_ref: int
    bind_request: str
    '''this has the format `1000_<channel_ref:8>_<?:8>`'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        channel_ref = parser.get_int()
        bind_request = parser.get_str()

        _ = parser.get_bytes(4)  # ?
        _ = parser.get_bytes(8)  # null
        _ = parser.get_bytes(8)  # ?
        _ = parser.get_bytes(8)  # ?

        return cls(
            header=header,
            channel_ref=channel_ref,
            bind_request=bind_request,
        )


@dataclass
class BindResponseMessage(Message, type_code=0x00020601):
    channel_ref: int
    bind_request: str
    '''this has the format `1000_<channel_ref:8>_<?:8>`'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        _ = parser.get_bytes(4)  # ?
        channel_ref = parser.get_int(4)
        bind_request = parser.get_str()
        _ = parser.get_bytes(4)  # ?
        _ = parser.get_bytes(12)  # ?

        return cls(
            header=header,
            channel_ref=channel_ref,
            bind_request=bind_request,
        )
