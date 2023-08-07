"""
This submodule defines message classes with default behaviors.
"""
from abc import ABC, abstractclassmethod, abstractmethod
from dataclasses import dataclass

from .utils import MessageParser

__all__ = [
    "Message",
    "MessageParser",
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
    def register_subclass(cls: 'type[MessageBase]', type_code=None) -> None:
        '''
        register a subclass to the central registry, so it can
        be accessesd at any time from anywhere
        '''
        __class__.TYPE_CODE_REGISTRY[type_code] = cls


@dataclass
class Message(MessageBase, ABC):
    @dataclass
    class MessageHeader:
        length: int
        id: int
        object_ref: int
        type_code: int

        def is_response(self):
            return bool(self.type_code & 1)

        def is_request(self):
            return not self.is_response()

    header: MessageHeader
    '''the header of the message. This is common to all messages'''

    @abstractclassmethod
    def parse(cls, header: 'Message.MessageHeader', parser: MessageParser):
        '''parse the raw data into a message'''
        raise NotImplementedError(
            f"{cls.__name__} has not implemented `parse`")


@dataclass
class UnknownMessageType(Message, type_code=0):
    '''any unknown message type should default into this type'''
    data: bytes

    @classmethod
    def parse(cls, header: Message.MessageHeader, parser: MessageParser):
        '''we cannot parse this message'''
        return cls(header=header, data=parser.data)
