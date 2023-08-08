from typing import Callable

from scapy.all import AsyncSniffer, Raw
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP


class TCPSniffer(AsyncSniffer):
    def __init__(self, host: str, port: int, callback: Callable[[bytes], None]) -> None:
        self.host = host
        self.port = port
        self.callback = callback
        super().__init__(filter='tcp', store=0, prn=self._callback,  iface='Ethernet')

    def _callback(self, pkt: Ether):
        # this is really bad and should be done with the filter instead.
        # I don't have the time to figure out how that works though
        if (not IP in pkt) or (pkt[IP].src != self.host):
            return
        if (not TCP in pkt) or (pkt[TCP].sport != self.port):
            return
        if not Raw in pkt:
            return
        try:
            self.callback(pkt[Raw].load)
        except Exception as e:
            print(e)
            pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
