import random
from dataclasses import dataclass, field


@dataclass
class NoisyChannel:
    bit_error_rate: float = 1e-3
    burst_length: int = 0
    word_swaps: int = 0
    byte_swaps: int = 0
    rng: random.Random = field(default_factory=random.Random)

    def transmit(self, frame: bytes) -> bytes:
        if self.word_swaps:
            return self._swap(frame, unit=2, count=self.word_swaps)
        if self.byte_swaps:
            return self._swap(frame, unit=1, count=self.byte_swaps)

        bits = bytearray(frame)
        nbits = len(bits) * 8

        if self.burst_length:
            start = self.rng.randrange(max(1, nbits - self.burst_length + 1))
            end = min(nbits, start + self.burst_length)
            positions = [i for i in range(start, end) if i in (start, end - 1) or self.rng.random() < 0.5]

        else:
            positions = [i for i in range(nbits) if self.rng.random() < self.bit_error_rate]

        for pos in positions:
            bits[pos // 8] ^= 0x80 >> (pos % 8)

        return bytes(bits)

    def _swap(self, frame: bytes, unit: int, count: int) -> bytes:
        data = bytearray(frame)
        nblocks = len(data) // unit
        if nblocks < 2:
            return bytes(data)

        for _ in range(count):
            i, j = (unit * k for k in self.rng.sample(range(nblocks), 2))
            data[i : i + unit], data[j : j + unit] = data[j : j + unit], data[i : i + unit]

        return bytes(data)
