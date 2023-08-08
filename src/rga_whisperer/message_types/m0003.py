"""
This submodule contains all messages whose type code starts with 0x0003.
"""
from dataclasses import dataclass

from .m0000 import Message, MessageParser

__all__ = [
    "UK_Request_1_Message",
    "UK_Response_1_Message",
]


@dataclass
class UK_Request_1_Message(Message, type_code=0x00030100):
    @dataclass
    class RequestObject:
        ref: int
        name: str

        @classmethod
        def parse(cls, parser: MessageParser):
            ref = parser.get_int()
            name = parser.get_str()
            while parser.get_bytes(4) != b"\xbf\x80\x00\x00":
                continue
            # _ = self.get_bytes(12)  # ?? this can be 8 or 12 long...
            # _ = self.get_bytes(4)  # b"\xbf\x80\x00\x00"
            return cls(
                ref=ref,
                name=name,
            )

    items: list[RequestObject]

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        nb_items = parser.get_int()
        items = [cls.RequestObject.parse(parser) for _ in range(nb_items)]

        return cls(
            header=header,
            items=items,
        )


@dataclass
class UK_Response_1_Message(Message, type_code=0x00030101):
    @dataclass
    class ResponseObject:
        ref: bytes
        dtype: int
        permission: int

        @classmethod
        def parse(cls, parser: MessageParser):
            error_code = parser.get_int()  # null
            if error_code:  # TODO : This is bad
                return cls(0, 0, 0)
            ref = parser.get_int()
            dtype = parser.get_int(2)
            _ = parser.get_bytes(2)  # ?
            # either \x01 or \x03 -> read/write permission ?
            permission = parser.get_int()
            _ = parser.get_bytes(8)
            _ = parser.get_bytes(4)  # b"\xbf\x80\x00\x00"
            return cls(
                ref=ref,
                dtype=dtype,
                permission=permission
            )

    items: list[ResponseObject]

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        _ = parser.get_bytes(4)  # null

        items = []
        while not parser.is_done():
            items.append(cls.ResponseObject.parse(parser))

        return cls(
            header=header,
            items=items,
        )
