from abc import ABC, abstractmethod


class Checksum(ABC):
    name: str
    width: int  # checksum size bytes

    @abstractmethod
    def compute(self, data: bytes) -> int: ...

    def to_bytes(self, value: int) -> bytes:
        return value.to_bytes(self.width, "big")

    def verify(self, data: bytes, expected: int) -> bool:
        return self.compute(data) == expected


# RFC 1071, 16-bit ones-complement sum
class InternetChecksum(Checksum):
    name = "internet"
    width = 2

    def compute(self, data: bytes) -> int:
        if len(data) % 2:
            data += b"\x00"

        total = 0
        for i in range(0, len(data), 2):
            total += (data[i] << 8) | data[i + 1]
            total = (total & 0xFFFF) + (total >> 16)

        return ~total & 0xFFFF


# Fletcher-16, two running mod255 sums, order matters
class Fletcher16(Checksum):
    name = "fletcher16"
    width = 2

    def compute(self, data: bytes) -> int:
        s1 = s2 = 0
        for b in data:
            s1 = (s1 + b) % 255
            s2 = (s2 + s1) % 255

        return (s2 << 8) | s1


# Adler-32, like Fletcher but mod65521 over 16bit sums
class Adler32(Checksum):
    name = "adler32"
    width = 4
    mod = 65521

    def compute(self, data: bytes) -> int:
        a, b = 1, 0
        for byte in data:
            a = (a + byte) % self.mod
            b = (b + a) % self.mod

        return (b << 16) | a


# CRC-32, reflected polynomial 0xEDB88320
class CRC32(Checksum):
    name = "crc32"
    width = 4
    poly = 0xEDB88320

    def __init__(self) -> None:
        self._table = [self._entry(i) for i in range(256)]

    def _entry(self, n: int) -> int:
        for _ in range(8):
            n = (n >> 1) ^ self.poly if n & 1 else n >> 1

        return n

    def compute(self, data: bytes) -> int:
        crc = 0xFFFFFFFF
        for b in data:
            crc = (crc >> 8) ^ self._table[(crc ^ b) & 0xFF]

        return crc ^ 0xFFFFFFFF


CHECKSUMS: dict[str, Checksum] = {
    c.name: c for c in (InternetChecksum(), Fletcher16(), Adler32(), CRC32())
}
