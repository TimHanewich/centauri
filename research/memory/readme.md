Mem used in read data: 16
Mem used in process lines: 16, but more rare
Mem used in move belt: 32, but rare

## Analyzing the pitch/roll angle trig
- `math.atan2()` = 60 us, 16 bytes
- `math.sqrt()` = 28 us, 16 bytes
- `1.43 / math.pi` = 8 us, 0 bytes