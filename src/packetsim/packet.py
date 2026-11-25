import struct
from dataclasses import dataclass

from .checksums import Checksum

HEADER = struct.Struct("!HHIH") # src port, dst port, sequence number, payload length


@dataclass
class Packet:
    src_port: int
    dst_port: int
    seq: int
    payload: bytes

    def body(self) -> bytes:
        return HEADER.pack(self.src_port, self.dst_port, self.seq, len(self.payload)) + self.payload

    def encode(self, checksum: Checksum) -> bytes:
        body = self.body()
        return body + checksum.to_bytes(checksum.compute(body))

    @staticmethod
    def check(frame: bytes, checksum: Checksum) -> bool:
        if len(frame) < HEADER.size + checksum.width:
            return False
        body, trailer = frame[: -checksum.width], frame[-checksum.width :]
        return checksum.verify(body, int.from_bytes(trailer, "big"))
