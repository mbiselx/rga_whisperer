from rga_whisperer.gui import Plotter, mkQApp
from rga_whisperer.interfaces import ethernet
from rga_whisperer.message_types import (
    parse_message,
    DataStream1Message, DataStream2Message,
    BindResponseMessage, UK_Request_1_Message,
)

HOST = ...
PORT = 56765

app = mkQApp('Ethernet Live Feed')
gui = Plotter()

# this is the COM object reference we need to look for
object_ref = -1
# this is the data item tag we need to look for
item_handle = -1


def callback(data):
    '''this function called for every COM data packet'''
    # use global variables because *that* never causes problems...
    global object_ref, item_handle

    msg = parse_message(data)

    # in the initial state, we don't know the object reference
    if isinstance(msg, (BindResponseMessage)):
        _, object_ref_str, _ = msg.bind_request.split('_')
        object_ref = int(object_ref_str, 16)
        print(f"{object_ref=}")
    elif object_ref < 0:
        return

    # once we kow the object ref, we can try to find the data item handle
    if isinstance(msg, UK_Request_1_Message):
        for item in msg.items:
            if item.name == 'Channels.Actuality.MeasureValue':
                item_handle = item.ref
                break
        print(f"{item_handle=}")
    elif item_handle < 0:
        return

    if isinstance(msg, (DataStream1Message, DataStream2Message)) and \
            msg.header.object_ref == object_ref:
        for e in msg.elements:
            if e.item_handle == item_handle and isinstance(e.value, list):
                gui.set_ydata(e.value)
                break


# the main program loop
with ethernet.TCPSniffer(HOST, PORT, callback) as sniffer:
    # start the GUI
    gui.show()

    # this is the event loop, which is responsible for the GUI.
    # it is run in the main thread
    app.exec()
