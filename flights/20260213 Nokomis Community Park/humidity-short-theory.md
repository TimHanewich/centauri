# Humidity Short Theory
As of Feb 14, 2026, this is the best theory I have to explain how the odd 99% packet *and* the poor receiving of telemetry happened (while also not being reproducable at home):

Look closely at how the drone's Rx code works, particularly the "conveyer belt" approach used. This could have happened.

1. The buffer is empty. Receiving is fine.
2. A short happens (heavy humidity from fog that day). Random data is caused and collected to buffer.
3. Then a valid packet is received with the \r\n terminator.
4. The code I have finds that \r\n terminator and thinks the "full line" was everything before it - **including the garbage!**
5. It doesn't pass the checksum so it "throws it out". So it *appears* it isn't getting new command data looking at the telemetry, but it *is*... it is just receiving command data **broken up by garbage caused by a short**, prompting most good data packets to be thrown away.

So how did the erroneous 99% packet happen? It is possible some garbage data got in front of an actual \r\n terminator and the XOR *happened* to match (1/256 random chance?) that whacko 99% throttle and -32% pitch and 0% roll and 0% yaw.

[This Claude chat](https://claude.ai/share/04fde4ac-4f0f-4162-bd11-726f4a050fc60) was helpful in validating this theory.