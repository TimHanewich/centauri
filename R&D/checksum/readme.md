# Updating Checksum to Two-Byte (from one byte)
The crash from February 13 2026 exposed that a singe-byte checksum can be very risky for over-air communication.

A single byte checksum is likely insufficient for over-the-air communication:
- 1-byte checksum = 0.4% chance of random pass (1/256)
- 2-byte checksum = 0.0015% chance of random pass (1/65536)

And as seen in [the 99% throttle anomaly from February 13, 2026](../../flights/20260213%20Nokomis%20Community%20Park/), I believe garbage data could be received *in between* a good packet, "taking the place of actual input data and then pass the checksum by chance.

So adding the second checksum makes it 256x less likely that a random pass will happen.