# UcComputerNetworkingProject
## Packet checksum simulator

Builds random packets (basically an 8-byte header + a payload + a checksum), sends them through a
noisy channel that flips bits, and counts how many corrupted packets each checksum
fals to catch.

| Name | Width | Used in |
|------|-------|---------|
| `internet` | 16-bit | IPv4 / TCP / UDP (RFC 1071) |
| `fletcher16` | 16-bit | Some legacy protocols, e.g. OSI transport, OSPF |
| `adler32` | 32-bit | zlib |
| `crc32` | 32-bit | Ethernet, PNG, zip |


### Run args
```sh
uv run packetsim
uv run packetsim --ber 0.01 -n 50000 
uv run packetsim --burst 40
uv run packetsim --swap 1
uv run pytest
```
