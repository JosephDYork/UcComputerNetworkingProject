import random
from dataclasses import dataclass, field


@dataclass
class NoisyChannel:
    bit_error_rate: float = 1e-3
    burst_length: int = 0
    word_swaps: int = 0
    rng: random.Random = field(default_factory=random.Random)

    def transmit(self, frame: bytes) -> bytes:
        if self.word_swaps:
            return self._swap_words(frame)

        bits = bytearray(frame)
        nbits = len(bits) * 8

        if self.burst_length:
            start = self.rng.randrange(max(1, nbits - self.burst_length + 1))
            positions = range(start, min(nbits, start + self.burst_length))
        else:
            positions = [i for i in range(nbits) if self.rng.random() < self.bit_error_rate]

        for pos in positions:
            bits[pos // 8] ^= 0x80 >> (pos % 8)

        return bytes(bits)

    def _swap_words(self, frame: bytes) -> bytes:
        data = bytearray(frame)
        nwords = len(data) // 2
        if nwords < 2:
            return bytes(data)

        for _ in range(self.word_swaps):
            i, j = (2 * w for w in self.rng.sample(range(nwords), 2))
            data[i : i + 2], data[j : j + 2] = data[j : j + 2], data[i : i + 2]

        return bytes(data)
