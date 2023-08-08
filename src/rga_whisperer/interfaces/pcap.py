import collections

from scapy.all import PcapReader, Raw
from scapy.layers.inet import IP, TCP

__all__ = [
    'read_pcap'
]


def read_pcap(filename: str):
    '''read a pcap file and yield the full RGA messages from it'''

    data_accumulator = collections.defaultdict(lambda: b'')

    with PcapReader(filename) as pcap_reader:
        for pkt in pcap_reader:
            if not (TCP in pkt) or not (Raw in pkt):
                # this packet does not fulfill our requirements
                continue

            data = pkt[Raw].load

            if len(data) < 16:
                # this packet is trivial and we don't care about it
                continue

            # accumulate data sequence
            data_accumulator[pkt[IP].src] += data

            if len(data) < 1460:
                # we can assume this packet is the last packet
                # of the sequence
                yield pkt[IP].src, data_accumulator[pkt[IP].src]

                # reset accumulator
                del data_accumulator[pkt[IP].src]
