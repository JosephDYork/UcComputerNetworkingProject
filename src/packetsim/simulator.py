import math
import random
from dataclasses import dataclass

from .channel import NoisyChannel
from .checksums import Checksum
from .packet import Packet


@dataclass
class SimulationResult:
    checksum: str
    sent: int = 0
    corrupted: int = 0
    detected: int = 0

    @property
    def undetected(self) -> int:
        return self.corrupted - self.detected

    @property
    def detection_rate(self) -> float:
        return self.detected / self.corrupted if self.corrupted else 1.0

    @property
    def undetected_rate(self) -> float:
        return self.undetected / self.corrupted if self.corrupted else 0.0

    @property
    def upper_bound_95(self) -> float:
        n, k = self.corrupted, self.undetected

        if n == 0:
            return 1.0

        if k == 0:
            return 3 / n

        z, p = 1.645, k / n
        return (p + z * z / (2 * n) + z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def simulate(
    checksum: Checksum,
    channel: NoisyChannel,
    packets: int = 1000,
    payload_size: int = 64,
    seed: int | None = None,
) -> SimulationResult:
    rng = random.Random(seed)
    result = SimulationResult(checksum.name)

    for seq in range(packets):
        pkt = Packet(
            src_port=rng.randrange(65536),
            dst_port=rng.randrange(65536),
            seq=seq,
            payload=rng.randbytes(payload_size),
        )

        sent = pkt.encode(checksum)
        received = channel.transmit(sent)
        result.sent += 1

        if received != sent:
            result.corrupted += 1
            if not Packet.check(received, checksum):
                result.detected += 1

    return result

