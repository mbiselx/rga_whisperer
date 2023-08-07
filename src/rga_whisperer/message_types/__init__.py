from .m0000 import *
from .m0002 import *
from .m0003 import *
from .m0004 import *


def parse_message(data: bytes) -> Message:
    '''parse some input data into a message'''

    # create a parser object for this message
    parser = MessageParser(data)

    # start by parsing the header
    header = Message.MessageHeader(*parser.get_value('iiii'))

    # from the header determine the type of message we need to parse
    message_class = Message.TYPE_CODE_REGISTRY.get(
        header.type_code,
        UnknownMessageType  # default to unknown message type
    )

    # instantiate a message class
    message = message_class.parse(
        header=header,
        parser=parser
    )

    return message
