"""
This submodule contains all messages whose type code starts with 0x0002.
"""
from dataclasses import dataclass

from .m0000 import Message, MessageParser, MessagePacker

__all__ = [
    "BrowseRequestMessage",
    "BrowseResponseMessage",
    "BindRequestMessage",
    "BindResponseMessage",
    "COMInitiateMessage",
    "COMResponseMessage",
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

    def pack_contents(self) -> bytes:
        return MessagePacker.make_str(self.item_name) + \
            MessagePacker.make_int(self.request_type, 12) + \
            bytes(16)


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

            def pack(self) -> bytes:
                raise NotImplementedError(
                    f"{self.__class__.__name__}: `pack`")

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

        def pack(self) -> bytes:
            short_name = MessagePacker.make_str(self.short_name)
            full_name = MessagePacker.make_str(self.full_name)
            item_type = MessagePacker.make_int(self.item_type)
            nb_subitems = MessagePacker.make_int(len(self.subitems), 8)
            subitems = sum(map(self.BrowseSubItems.pack,
                           self.subitems), start=b'')
            padding = bytes(4) if len(self.subitems) else b''
            return short_name + full_name + item_type + nb_subitems + subitems + padding

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

    def pack_contents(self) -> bytes:
        items = sum(map(self.BrowseItems.pack, self.items), start=b'')
        return bytes(8) + MessagePacker.make_int(len(self.items), 8) + items


@dataclass
class BindRequestMessage(Message, type_code=0x00020600):
    item_handle: int
    bind_request: str
    '''this has the format `{???}_{item_handle:08.x}_{?:07.x}`'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        item_handle = parser.get_int()
        bind_request = parser.get_str()

        _ = parser.get_bytes(4)  # ?
        _ = parser.get_bytes(8)  # null
        _ = parser.get_bytes(8)  # ?
        _ = parser.get_bytes(8)  # ?

        return cls(
            header=header,
            item_handle=item_handle,
            bind_request=bind_request,
        )

    def pack_contents(self) -> bytes:
        return MessagePacker.make_int(self.item_handle) + \
            MessagePacker.make_str(self.bind_request) + \
            bytes(28)


@dataclass
class BindResponseMessage(Message, type_code=0x00020601):
    item_handle: int
    bind_request: str
    '''this has the format `{???}_{item_handle:08.x}_{?:07.x}`'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        _ = parser.get_bytes(4)  # ?
        item_handle = parser.get_int(4)
        bind_request = parser.get_str()
        _ = parser.get_bytes(4)  # ?
        _ = parser.get_bytes(12)  # ?

        return cls(
            header=header,
            item_handle=item_handle,
            bind_request=bind_request,
        )

    def pack_contents(self) -> bytes:
        return bytes(4) + MessagePacker.make_int(self.item_handle) + \
            MessagePacker.make_str(self.bind_request) + \
            bytes(16)


@dataclass
class COMInitiateMessage(Message, type_code=0x00020800):
    connection_name: str

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        connection_name = parser.get_str()

        return cls(
            header=header,
            connection_name=connection_name,
        )

    def pack_contents(self) -> bytes:
        return MessagePacker.make_str(self.connection_name)


@dataclass
class COMResponseMessage(Message, type_code=0x00020801):
    data: bytes

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        data = parser.get_bytes(4)

        return cls(
            header=header,
            data=data,
        )

    def pack_contents(self) -> bytes:
        return self.data
