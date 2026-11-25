import argparse
import random

from .channel import NoisyChannel
from .checksums import CHECKSUMS
from .simulator import simulate

# python -m packetsim [options]
def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Compare checksum error detection over a noisy channel.")
    p.add_argument("-n", "--packets", type=int, default=10_000)
    p.add_argument("-s", "--payload-size", type=int, default=64)
    p.add_argument("-b", "--ber", type=float, default=1e-3, help="bit error rate")
    p.add_argument("--burst", type=int, default=0, help="burst error length in bits (overrides --ber)")
    p.add_argument("--swap", type=int, default=0, help="swap N pairs of 16-bit words per packet (overrides --ber/--burst)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("-c", "--checksum", choices=CHECKSUMS, action="append", help="checksum(s) to test (default: all)")
    args = p.parse_args(argv)

    print(f"{'checksum':<12}{'sent':>8}{'corrupt':>9}{'detected':>10}{'missed':>8}{'rate':>10}")

    for name in args.checksum or CHECKSUMS:
        channel = NoisyChannel(args.ber, args.burst, args.swap, random.Random(args.seed))
        r = simulate(CHECKSUMS[name], channel, args.packets, args.payload_size, args.seed)

        print(f"{r.checksum:<12}{r.sent:>8}{r.corrupted:>9}{r.detected:>10}"
              f"{r.undetected:>8}{r.detection_rate:>10.2%}")


if __name__ == "__main__":
    main()
