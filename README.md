# UcComputerNetworkingProject
Joseph and Soumya's Computer Networking Project and presentation

## Packet checksum simulator

Builds random packets (8-byte header + payload + checksum), sends them through a
noisy channel that flips bits, and counts how many corrupted packets each checksum
fails to catch.

Checksums compared (`src/packetsim/checksums.py`):

| Name | Width | Used in |
|------|-------|---------|
| `internet` | 16-bit | IPv4 / TCP / UDP (RFC 1071) |
| `fletcher16` | 16-bit | Some legacy protocols, e.g. OSI transport, OSPF |
| `adler32` | 32-bit | zlib |
| `crc32` | 32-bit | Ethernet, PNG, zip |

### Run

```sh
uv run packetsim                      # all checksums, random bit errors
uv run packetsim --ber 0.01 -n 50000  # heavier noise
uv run packetsim --burst 40           # burst errors of 40 bits
uv run packetsim --swap 1             # swap two 16-bit words per packet
uv run pytest
```

### Layout

- `packet.py`: packet format, encoding, and the receiver-side check
- `channel.py`: noisy channel (random bit flips, burst errors, or 16-bit word swaps)
- `checksums.py`: the four algorithms plus a `CHECKSUMS` registry
- `simulator.py`: runs the experiment and collects detection stats
- `main.py`: CLI that prints a comparison table
