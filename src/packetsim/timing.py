import random
import time
from dataclasses import dataclass

from .checksums import Checksum
from .packet import Packet


@dataclass
class TimingResult:
    checksum: str
    payload_size: int
    packets: int
    total_bytes: int
    elapsed_ns: int

    @property
    def ns_per_byte(self) -> float:
        return self.elapsed_ns / self.total_bytes

    @property
    def mb_per_s(self) -> float:
        return self.total_bytes / (self.elapsed_ns / 1e9) / 1e6


def measure_throughput(
    checksum: Checksum, payload_size: int, packets: int = 10_000, repeats: int = 3, seed: int = 0
) -> TimingResult:
    best = None
    rng = random.Random(seed)
    compute = checksum.compute
    bodies = [Packet(rng.randrange(65536), rng.randrange(65536), seq, rng.randbytes(payload_size)).body()
        for seq in range(packets)]

    for _ in range(repeats):
        start = time.perf_counter_ns()
        for body in bodies:
            compute(body)

        elapsed = time.perf_counter_ns() - start
        best = elapsed if best is None else min(best, elapsed)

    return TimingResult(checksum.name, payload_size, packets, sum(map(len, bodies)), best)
