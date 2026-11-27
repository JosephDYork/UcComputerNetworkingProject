# UcComputerNetworkingProject
## Packet checksum simulator

Builds random packets (a 10-byte header + a payload + a checksum), sends them through a
noisy channel that corrupts them, and counts how many corrupted packets each checksum
fails to catch. The checksums compared are the Internet Checksum, Fletcher-16, Adler-32 and CRC-32.

### Run args
```sh
uv run packetsim                                          # random bit flips
uv run packetsim --ber 0.01 -n 50000                      # higher bit error rate
uv run packetsim --burst 40                               # one 40-bit burst error per packet
uv run packetsim --swap 1                                 # swap two 16-bit words per packet
uv run packetsim --byte-swap 1                            # swap two single bytes unaligned
uv run packetsim -s 16,64,256                             # run at several payload sizes
uv run packetsim --sweep-burst -s 16,256 -n 5000          # burst lengths 1-40 at each size
uv run packetsim --sweep-burst 1-48                       # custom burst range
uv run packetsim --collisions -s 0,8,32,128,512 -n 50000  # effective checksum bits by payload size
uv run packetsim --timing -s 16,256,1024 -n 2000          # processing latency in ns/byte & MB/s
uv run packetsim --sweep-burst --csv results.csv          # also save the results to a CSV file
uv run packetsim -c crc32 -c adler32                      # only test the named checksums
```

### Options
| Option | Default | Meaning |
|---|---|---|
| `-n`, `--packets` | 10000 | packets per run (random samples for `--collisions`) |
| `-s`, `--payload-size` | 64 | payload size(s) in bytes, comma separated |
| `-b`, `--ber` | 0.001 | probability that each bit flips |
| `--burst L` | off | one burst of L bits per packet: first and last bits flipped, bits in between random |
| `--swap N` | off | swap N random pairs of 16-bit-aligned words per packet |
| `--byte-swap N` | off | swap N random pairs of single bytes at any position (unaligned) |
| `--sweep-burst [MIN-MAX]` | 1-40 | run every burst length in the range |
| `--collisions` | off | count packets that share a checksum value and report effective bits |
| `--timing` | off | time each checksum and report ns/byte and MB/s (best of 3 runs) |
| `-c`, `--checksum` | all | `internet`, `fletcher16`, `adler32` or `crc32`; repeatable |
| `--seed` | 0 | random seed, so runs are repeatable |
| `--csv PATH` | off | also write the results to a CSV file |
