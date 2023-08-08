import time
from threading import Thread

from rga_whisperer.interfaces import pcap
from rga_whisperer.gui import Plotter, mkQApp
from rga_whisperer.message_types import *

filename = ...

app = mkQApp('Ethernet Live Feed')
gui = Plotter()


def run():
    '''this function is run by the thread, to prevent blocking the GUI'''
    for _, data in pcap.read_pcap(filename):
        msg = parse_message(data)

        if isinstance(msg, (DataStream1Message, DataStream2Message)):
            if msg.header.object_ref == 120827608:
                for e in msg.elements:
                    if e.item_handle == 116579336 and isinstance(e.value, list):
                        gui.set_ydata(e.value)
                        break
                time.sleep(.5)


thread = Thread(target=run, daemon=True)

# start the GUI
gui.show()

# start the pcap-reading thread
thread.start()

# this is the event loop, which is responsible for the GUI.
# it is run in the main thread
app.exec()
