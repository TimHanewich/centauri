# Humidity Short Theory
As of Feb 14, 2026, this is the best theory I have to explain how the odd 99% packet *and* the poor receiving of telemetry happened (while also not being reproducable at home):

## Likely Cause (Theory)
During this day of fying there was an exceptional degree of humidity in the air that day (~85% due to heavy fog). I theorize that moisture built up on the HC-12 between the pin wires. This short caused occasional random data to appear at times, tempermentally.

My transmitter would be transmitting *good data*, which would be received by the drone and read. However, in between receiving this data, it would also get batches of random data likely caused by this short. So, the good data was occasionally "broken up" by bad data.

In most cases, the good data with the bad data woud *not* pass the checksum and thus would be "thrown away". However, in the particular case of this crash here is what I think happened: good data was received, then *bad data* was received, but then *good data* was received for the **tail end** of the packet (roll rate, yaw rate, checksum, terminator). The "garbage bytes" that came before *happened* to pass the checksum. The checksum is only one byte, so really there is a 1/256 chance that it passes randomly; this is *not* enough for over-the-air! 

Anyway, the garbage bytes that came before the good bytes were interpreted lierally: as 99% throttle and -32% pitch!

So, the checksum passed (the garbage throttle & pitch byes matched the checksum), it enacted that packet, and then received a *real* data packet just after, correting everything to legitimate input I had been giving it.

But then it did not receive anything for a number of seconds! Why is that? Because of the short! It probably continued getting garbage data which caused all the good data to be "broken up" by bad data, failing checksums, and "thrown out"... **so the problem wasnt it not *receiving data* (it was receving!), it was the short causing the data to be broken up by garbage data, most of it getting thrown out, but one unlucky case of a corrupted (half garbage, half real) paket passing the checksum!**

[This Claude chat](https://claude.ai/share/04fde4ac-4f0f-4162-bd11-726f4a050fc60) was helpful in validating this theory.

## Rx Buffer Full Risk
Look closely at how the drone's Rx code works, particularly the "conveyer belt" approach used. This could happen too.

Remember, data that is received but not received of a \r\n terminator is staying in the rx buffer. It is possible for that Rx buffer to fill up so much with incomplete / bad data that it reaches capacity and thus is no longer accepting new *good* data! 

To mitigate this, put like a 80% dump logic in... if the rx buffer (process buffer) gets to 80% capacity and we still don't have a \r\n terminator, dump (clear) it!


## Improvements to make if really believe this to be true
1. Implement two-byte checksum. This reduces likelihood of random checksum pass from 0.4% (1/256) to 0.0015% (1/65,536).
2. Implement Rx Buffer (process buffer) "dumping" logic if it gets too full.
3. Maybe telemetry recording of how big that process buffer is, or better yet, how many actual BYTES have been received in total... that would be helpful for diagnosing problems like this.