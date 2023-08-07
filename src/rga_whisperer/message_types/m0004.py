"""
This submodule contains all messages whose type code starts with 0x0004.
"""
import struct
from dataclasses import dataclass
from datetime import datetime

from .utils import DTYPE_ARRAY_BITMASK, DTYPE_LOOKUP
from .m0000 import Message, MessageParser

__all__ = [
    "DataStream1Message",
    "DataStream2Message"
]


@dataclass
class DataStreamMessage(Message, type_code=0x00040000):
    @dataclass
    class DataElement:
        item_handle: int
        value: list | None
        quality: int
        timestamp: datetime

        @classmethod
        def parse(cls, parser: MessageParser):

            item_handle = parser.get_int()
            _ = parser.get_bytes(4)  # null
            dtype = parser.get_int(2)

            is_array = bool(dtype & DTYPE_ARRAY_BITMASK)
            dtype_code = DTYPE_LOOKUP[dtype & ~DTYPE_ARRAY_BITMASK]

            if is_array:
                _ = parser.get_bytes(2)  # always pad
                value = parser.get_array(dtype_code)
            else:
                dsize = struct.calcsize(dtype_code)
                if dsize > 2:
                    dtype_code = 'xx'+dtype_code  # prepend two padding bytes
                elif dsize < 2:
                    dtype_code += 'x'  # append a padding byte
                value = parser.get_value(dtype_code)

            quality = parser.get_int(2)
            _ = parser.get_bytes(2)  # ??
            timestamp = parser.get_timestamp()

            return cls(
                item_handle=item_handle,
                value=value,
                quality=quality,
                timestamp=timestamp
            )

    elements: list[DataElement]
    '''list of the data elements contained in this message'''

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):

        _ = parser.get_bytes(12)  # null
        nb_elem = parser.get_int(4)  # probably item count
        elements = [cls.DataElement.parse(parser) for _ in range(nb_elem)]

        return cls(
            header=header,
            elements=elements,
        )


class DataStream1Message(DataStreamMessage, type_code=0x00040100):
    '''duplicate of DataStream message with a different code'''
    pass


class DataStream2Message(DataStreamMessage, type_code=0x00040200):
    '''duplicate of DataStream message with a different code'''
    pass
