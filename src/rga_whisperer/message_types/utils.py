import struct
from datetime import datetime, timedelta


DTYPE_LOOKUP = {
    0x02: 'h',  # signed short
    0x04: 'f',  # single-precision floating point
    # 0x07 : datetime
    # 0x08 : string
    0x11: 'b',  # single unsigned character
    0x12: 'H',  # unsigned short
}
DTYPE_ARRAY_BITMASK = 0x2000

TIME_ORIGIN = datetime(
    year=1601,
    month=1,
    day=1,
    hour=0,
    minute=0,
    second=0,
    microsecond=0
)


class MessageParser:
    '''
    This class implements some basic parsing utilities, 
    and tracks parsing progress on raw data with an internal pointer.
    '''

    def __init__(self, data: bytes) -> None:
        self.data = data
        '''the full copy of the data'''
        self.ptr = 0
        '''internal pointer used for parsing. do not touch!'''

    def get_bytes(self, size=4, pad=False) -> bytes:
        b = self.data[self.ptr: self.ptr + size]
        self.ptr += size
        if pad and (pad_required := self.ptr % 4):  # pad to nearest word
            self.ptr += 4-pad_required
        return b

    def get_value(self, dtype: str):
        val = struct.unpack('>'+dtype, self.get_bytes(struct.calcsize(dtype)))
        return val

    def get_array(self, dtype: str) -> list:
        _ = self.get_bytes(4)  # \x00\x01\x00\x00
        nb_elem = self.get_int()
        _ = self.get_bytes(4)  # null
        fmstr = nb_elem*dtype
        return list(*struct.iter_unpack('>'+fmstr, self.get_bytes(struct.calcsize(fmstr))))

    def get_int(self, size=4) -> int:
        return int.from_bytes(self.get_bytes(size), 'big')

    def get_str(self) -> str:
        n_chars = self.get_int()
        s = self.get_bytes(n_chars, True).decode('ascii')
        return s

    def get_timestamp(self) -> datetime:
        # we expect it to be in 100 ns increments (according to datasheet)
        # but it's actually in 1 us increments ...
        s = int.from_bytes(self.get_bytes(8), 'big', signed=True) * 1e-6
        ts = timedelta(seconds=s)
        return TIME_ORIGIN + ts
