import math
import random
from collections.abc import Iterable
from dataclasses import dataclass

from .channel import NoisyChannel
from .checksums import Checksum
from .packet import Packet
from .simulator import SimulationResult, simulate


@dataclass
class BurstRow:
    payload_size: int
    burst_length: int
    result: SimulationResult


def burst_sweep(
    checksums: Iterable[Checksum],
    lengths: Iterable[int],
    sizes: Iterable[int],
    packets: int = 1000,
    seed: int = 0,
) -> list[BurstRow]:
    rows = []
    checksums, lengths = list(checksums), list(lengths)
    for size in sizes:
        for length in lengths:
            for c in checksums:
                channel = NoisyChannel(burst_length=length, rng=random.Random(seed))
                rows.append(BurstRow(size, length, simulate(c, channel, packets, size, seed)))

    return rows


@dataclass
class CollisionResult:
    checksum: str
    payload_size: int
    samples: int
    collisions: int

    @property
    def pairs(self) -> int:
        return self.samples * (self.samples - 1) // 2

    @property
    def effective_bits(self) -> float:
        return math.log2(self.pairs / self.collisions) if self.collisions else math.inf


def collision_test(checksum: Checksum, payload_size: int, samples: int = 50_000, seed: int = 0) -> CollisionResult:
    rng = random.Random(seed)
    counts: dict[int, int] = {}
    collisions = 0

    for seq in range(samples):  # unique seq numbers, so every packet is distinct
        body = Packet(rng.randrange(65536), rng.randrange(65536), seq, rng.randbytes(payload_size)).body()
        value = checksum.compute(body)
        collisions += counts.get(value, 0)
        counts[value] = counts.get(value, 0) + 1

    return CollisionResult(checksum.name, payload_size, samples, collisions)
