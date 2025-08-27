# HC-12 Half-Duplex Issue
I encountered an issue while building out the receiving coroutine on the HL-MCU, after having already established the sending coroutine on the HL-MCU. 

That issue? The HC-12 *cannot* receive and send data at the same time. In other words, if the HC-12 is *sending* data at the same time that data is *arriving*, that arriving data will be completely missed. And not available in the UART buffer of the Pi, because the HC-12 never even received it and decoded it; it was busy sending!

![issue](https://i.imgur.com/wjJHBfI.png)

![issue2](https://i.imgur.com/7O67AIL.png)

## Possible Solution: Use two HC-12s
A pretty good suggestion [from here on Stack Exchange](https://arduino.stackexchange.com/questions/80914/can-we-have-2-hc12-on-a-single-arduino-1-to-receive-and-other-to-transmit): simply use two HC-12s... one for Rx, one for Tx. From the same UART interface on the Pi, but just hooking up the Rx pin to one and the Tx pin to the other.

![suggestion](https://i.imgur.com/mdCAz8y.png)

This brings up a new set of challenges, however:
- Would not be able to AT command with either, so no configuration of either. Needs to be configured before being permanently wired into the system.
- Unable to get a "pulse" to confirm the HC-12 is connected

## Possible Solution: Massively Reduce SENDING of Data
The issue I am most worried about is the HL-MCU (drone) *not* receiving control packet updates. This can be bad and possibly dangerous. 

So, to mitigate the risk of a large number of packets *not* being received because the HC-12 onboard the drone was busy transmitting telemetry data back to the controller, just have it transmit telemetry data much less frequently. 

My previous goal:
- Remote controller sends control packets @ 30 Hz
- Drone sends telemetry updates @ 10 Hz

Maybe a better goal:
- Remote controller sends control packets @ 30 Hz
- Drone sends telemetry updates **@ 1 Hz**

Only sending it at 1 Hz means for sure some of the incoming control data *will* be dropped, but only very few.

Another good goal to prevent interuption of large packets is to vary the frequency of that telemetry coming in based on whether the drone is armed or not. When armed, telemetry should be coming off of it rather continuously, like 1 time per second. But when not armed, it could be reduced to once ever 3-5 seconds probably.