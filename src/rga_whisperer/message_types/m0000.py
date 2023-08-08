"""
This submodule defines message classes with default behaviors.
"""
from abc import ABC, abstractclassmethod
from dataclasses import dataclass

from .utils import MessageParser, MessagePacker

__all__ = [
    "Message",
    "MessageParser",
    "MessagePacker",
    "UnknownMessageType",
]

# we first create the base class, so that all subclassed messages
# can be made as dataclasses


class MessageBase():
    '''
    abstract base class of a message. musts be subclassed for use
    '''
    TYPE_CODE_REGISTRY: 'dict[int, type[MessageBase]]' = {}
    '''central registry for all Message type codes'''
    type_code = 0  # default is 0
    '''type code for this message class'''

    def __init_subclass__(cls, type_code: int | None = None) -> None:
        # when a subclass is created, it is automatically registered
        #  with the relevant type code
        if type_code:
            cls.type_code = type_code
        __class__.register_subclass(cls, cls.type_code)
        return super().__init_subclass__()

    @staticmethod
    def register_subclass(subcls: 'type[MessageBase]', type_code: int) -> None:
        '''
        register a subclass to the central registry, so it can
        be accessesd at any time from anywhere
        '''
        __class__.TYPE_CODE_REGISTRY[type_code] = subcls


@dataclass
class Message(MessageBase, ABC):
    @dataclass
    class MessageHeader:
        length: int = 16
        id: int = 0
        object_ref: int = 0
        type_code: int = 0

        def is_response(self):
            return bool(self.type_code & 1)

        def is_request(self):
            return not self.is_response()

        def pack(self) -> bytes:
            return MessagePacker.make_int(self.length) + \
                MessagePacker.make_int(self.id) + \
                MessagePacker.make_int(self.object_ref) + \
                MessagePacker.make_int(self.type_code)

    header: MessageHeader
    '''the header of the message. This is common to all messages'''

    @abstractclassmethod
    @classmethod
    def parse(cls, header: 'Message.MessageHeader', parser: MessageParser):
        '''parse the raw data into a message'''
        raise NotImplementedError(
            f"{cls.__name__} has not implemented `parse`")

    def pack_contents(self) -> bytes:
        '''internal helper function for packing. should be overwritten by subclasses'''
        raise NotImplementedError(
            f"{self.__class__.__name__} has not implemented `pack_contents`")

    def pack(self, id=None) -> bytes:
        '''pack a message into bytes'''
        packed_msg = self.pack_contents()
        if id:
            self.header.id = id
        self.header.length = len(packed_msg) + 16
        self.header.type_code = self.type_code
        return self.header.pack() + packed_msg


@dataclass
class UnknownMessageType(Message, type_code=0):
    '''any unknown message type should default into this type'''
    data: bytes

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        '''we cannot parse this message'''
        return cls(header=header, data=parser.data)

    def pack_contents(self) -> bytes:
        return self.data
