# UcComputerNetworkingProject
## Packet checksum simulator

Builds random packets (basically an 8-byte header + a payload + a checksum), sends them through a
noisy channel that flips bits, and counts how many corrupted packets each checksum
fals to catch.

### Run args
```sh
uv run packetsim
uv run packetsim --ber 0.01 -n 50000 
uv run packetsim --burst 40
uv run packetsim --swap 1
uv run pytest
```
