import argparse
import csv
import random

from .channel import NoisyChannel
from .checksums import CHECKSUMS
from .simulator import simulate
from .sweep import burst_sweep, collision_test
from .timing import measure_throughput


def parse_sizes(text: str) -> list[int]:
    """'16,64,256' -> [16, 64, 256]"""
    return [int(s) for s in text.split(",")]


def parse_range(text: str) -> range:
    """'1-32' -> 1..32 inclusive, '8' -> just 8"""
    lo, _, hi = text.partition("-")
    return range(int(lo), int(hi or lo) + 1)


def write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {len(rows)} rows to {path}")


def result_fields(r) -> dict:
    return dict(checksum=r.checksum, sent=r.sent, corrupted=r.corrupted, detected=r.detected,
                missed=r.undetected, miss_rate=r.undetected_rate, upper_95=r.upper_bound_95)


def run_single(args, names) -> list[dict]:
    rows = []
    print(f"{'size':>6}  {'checksum':<12}{'sent':>8}{'corrupt':>9}{'detected':>10}{'missed':>8}"
          f"{'miss rate':>11}{'95% upper':>11}")
    for size in args.payload_size:
        for name in names:
            channel = NoisyChannel(args.ber, args.burst, args.swap, args.byte_swap, random.Random(args.seed))
            r = simulate(CHECKSUMS[name], channel, args.packets, size, args.seed)
            print(f"{size:>6}  {r.checksum:<12}{r.sent:>8}{r.corrupted:>9}{r.detected:>10}{r.undetected:>8}"
                  f"{r.undetected_rate:>11.2e}{r.upper_bound_95:>11.2e}")
            rows.append(dict(payload_size=size, **result_fields(r)))
    print("\n95% upper = one-sided 95% bound on the miss rate (rule of three, 3/N, when nothing was missed)")
    return rows


def run_burst_sweep(args, names) -> list[dict]:
    rows = burst_sweep([CHECKSUMS[n] for n in names], args.sweep_burst, args.payload_size, args.packets, args.seed)
    by_cell = {(r.payload_size, r.burst_length, r.result.checksum): r.result for r in rows}
    for size in args.payload_size:
        print(f"\npayload {size} bytes: missed bursts out of {args.packets} packets per length")
        print(f"{'burst':>5}" + "".join(f"{n:>12}" for n in names))
        for length in args.sweep_burst:
            print(f"{length:>5}" + "".join(f"{by_cell[size, length, n].undetected:>12}" for n in names))
    n = args.packets
    print(f"\n0 missed = none in {n} trials; 95% upper bound on the miss rate ≈ 3/{n} = {3 / n:.1e} (rule of three)")
    return [dict(payload_size=r.payload_size, burst_length=r.burst_length, **result_fields(r.result)) for r in rows]


def run_collisions(args, names) -> list[dict]:
    rows = []
    print(f"effective checksum bits from {args.packets} random packets (ideal N-bit checksum scores N)")
    print(f"{'size':>6}" + "".join(f"{n:>12}" for n in names))
    for size in args.payload_size:
        results = [collision_test(CHECKSUMS[n], size, args.packets, args.seed) for n in names]
        print(f"{size:>6}" + "".join(f"{r.effective_bits:>12.1f}" for r in results))
        rows += [dict(payload_size=size, checksum=r.checksum, samples=r.samples,
                      collisions=r.collisions, effective_bits=round(r.effective_bits, 2)) for r in results]
    return rows


def run_timing(args, names) -> list[dict]:
    rows = []
    print(f"processing latency, best of 3 runs over {args.packets} packets (pure Python)")
    print(f"{'size':>6}  {'checksum':<12}{'ns/byte':>10}{'MB/s':>10}")
    for size in args.payload_size:
        for name in names:
            r = measure_throughput(CHECKSUMS[name], size, args.packets, seed=args.seed)
            print(f"{size:>6}  {r.checksum:<12}{r.ns_per_byte:>10.1f}{r.mb_per_s:>10.2f}")
            rows.append(dict(payload_size=size, checksum=r.checksum, packets=r.packets, total_bytes=r.total_bytes,
                             elapsed_ns=r.elapsed_ns, ns_per_byte=round(r.ns_per_byte, 2),
                             mb_per_s=round(r.mb_per_s, 3)))
    return rows


# uv run packetsim [options]
def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Compare checksum error detection over a noisy channel.")
    p.add_argument("-n", "--packets", type=int, default=10_000, help="packets per run (samples for --collisions)")
    p.add_argument("-s", "--payload-size", type=parse_sizes, default=[64],
                   help="payload size(s) in bytes, comma separated, e.g. 16,64,256")
    p.add_argument("-b", "--ber", type=float, default=1e-3, help="bit error rate")
    p.add_argument("--burst", type=int, default=0, help="burst error length in bits (overrides --ber)")
    p.add_argument("--swap", type=int, default=0, help="swap N pairs of 16-bit words per packet (overrides --ber/--burst)")
    p.add_argument("--byte-swap", type=int, default=0,
                   help="swap N pairs of single bytes at any position, unaligned (overrides --ber/--burst)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("-c", "--checksum", choices=CHECKSUMS, action="append", help="checksum(s) to test (default: all)")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--sweep-burst", type=parse_range, nargs="?", const=range(1, 41), metavar="MIN-MAX",
                      help="sweep burst lengths (default 1-40, past CRC-32's 32-bit guarantee) at each payload size")
    mode.add_argument("--collisions", action="store_true",
                      help="measure checksum collisions between random packets at each payload size")
    mode.add_argument("--timing", action="store_true", help="measure processing latency (ns/byte, MB/s) at each payload size")
    p.add_argument("--csv", metavar="PATH", help="also write the results to a CSV file")
    args = p.parse_args(argv)

    names = args.checksum or list(CHECKSUMS)
    if args.sweep_burst:
        rows = run_burst_sweep(args, names)
    elif args.collisions:
        rows = run_collisions(args, names)
    elif args.timing:
        rows = run_timing(args, names)
    else:
        rows = run_single(args, names)

    if args.csv:
        write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
