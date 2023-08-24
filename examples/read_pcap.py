import time
from threading import Thread

from rga_whisperer.interfaces import pcap
from rga_whisperer.gui import Plotter, mkQApp
from rga_whisperer.message_types import (
    parse_message,
    DataStream1Message, DataStream2Message,
    BindResponseMessage, UK_Request_1_Message,
)

filename = ...

app = mkQApp('PCAP Playback')
gui = Plotter()


def run():
    '''this function is run by the thread, to prevent blocking the GUI'''

    # this is the COM object reference we need to look for
    object_ref = -1
    # this is the data item tag we need to look for
    item_handle = -1

    for _, data in pcap.read_pcap(filename):
        msg = parse_message(data)

        # in the initial state, we don't know the object reference
        if isinstance(msg, (BindResponseMessage)):
            _, object_ref_str, _ = msg.bind_request.split('_')
            object_ref = int(object_ref_str, 16)
            print(f"{object_ref=}")
        elif object_ref < 0:
            continue

        # once we kow the object ref, we can try to find the data item handle
        if isinstance(msg, UK_Request_1_Message):
            for item in msg.items:
                if item.name == 'Channels.Actuality.MeasureValue':
                    item_handle = item.ref
                    break
            print(f"{item_handle=}")
        elif item_handle < 0:
            continue

        # only data stream messages will be of any use
        if isinstance(msg, (DataStream1Message, DataStream2Message)) and \
                msg.header.object_ref == object_ref:
            for e in msg.elements:
                if (e.item_handle == item_handle) and \
                        isinstance(e.value, list):
                    gui.set_ydata(e.value)
                    break
            time.sleep(.1)  # give the plot time to update

    print("done")


# the main program loop runs in a separate thread
thread = Thread(target=run, daemon=True)

# start the GUI
gui.show()

# start the pcap-reading thread
thread.start()

# this is the event loop, which is responsible for the GUI.
# it is run in the main thread
app.exec()
