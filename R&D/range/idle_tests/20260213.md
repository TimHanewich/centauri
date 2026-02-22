# Idle Tests
I loaded a simple script to the drone to have it idle at 30% motor speed (props off) to test noise at 433 MHz band using the RTL-SDR.

In my tests. I was on the 433.8 MHz band on the RTL-SDR. There are a few seconds of nothing to begin with in each test recording (before I plugged in the drone), but then you see that broad spectrum blip when the drones motors start running.

In all of these tests, the drone is *not* transmitting anything via the HC-12. The script is simple: it only puts the motors at 30%.

I ran three tests with the following results:
- Test 1
    - No antenna is in the drone. Just empty SMA port.
    - Some noise from ESCs and motors in vicinity, but mild.
    - If I hold the RTL-SDR antenna close to the empty SMA port on the drone, a lot of noise near it.
- Test 2
    - Screwed in a 433 MHz antenna (1.29 SWR) into the SMA port on the drone.
    - The noise in the vicinity is a tad better.
    - But holding the SWR antenna so close to the drone's 433 MHz antenna caused a LOT of noise. A lot of red, especially when I am very very close to the 433 MHz antenna (basically touching it).
- Test 3
    - This was the only test I *also* had the 5.8 GHz AIO module plugged in (on the same power supply as the rest of the drones electronics)
    - 433 MHz antenna is also still plugged into it.
    - When idling, noise actually seems quite minimal in the vicinity (inches away)
    - When I hold the RTL-SDR's antenna to the AIO module's 5.8 GHz little antenna, **very** noisy. All red! Complete cut off.
    - But then holding the RTL-SDR's antennna to the drone's 433 MHz antenna didn't really have much noise at all. Weird!
    - *So why would the noise be LESS when the AIO module is plugged in? Is the AIO module "starving" the other components for power?*
- Test 4
    - In this test I had the 433 MHz antenna plugged in, not the AIO module
    - In this test I updated the script so it would idle motors at 30% for 5 seconds, then turn off for 5 seconds, then repeat
    - Again holding the RTL-SDR's antenna close to the drone's antenna, there doesnt appear to be a difference in noise when the motors are running vs. not running.
    - So I do not think it is necessarily current running through the wires as there wasnt really any current running at that time.
    - Is this still caused by "switching" by the ESCs, just at a 1,000,000 (0%) ns PWM?
- Test 5
    - 433 MHz antenna in, AIO module off.
    - Removed the test script entirely. Motors won't run at all now!
    - When plugged in, ESCs get power, but are not armed whatsoever (no PWM signal at all). They just sit idle.
    - I was touching the RTL-SDR antenna to the drone's antenna. You can still see a noise floor.
    - However, noise floor much less. 
    - So: I think the ESCs causing much of this noise. Even with no PWM signal, some noise... but even at 0% throttle, still "switching" at 250 Hz and thus a lot of noise from that!

So there definitely appears to be noise occuring, but the question is, is it from:
1. The exposed wires radiating noise
2. The HC-12 itself is getting a "dirty" power supply, affected by the ESCs and such and it is "radiating" like an exhaust pipe out the antenna

I believe it is #2. The noise appears to be coming from within, probably caused by the "dirty" switching ESCs.

*Note: testing the RTL-SDR's 433 MHz antenna touching an unpowered 433 MHz antenna does nothing. No effect. So the noise definitely caused by electronics.*

## Test Results Video
I recorded the RTL-SDR feed for each test, find that [here](https://www.youtube.com/watch?v=AejCrw2K9II).

## AI Help
Prompt:
```
I am developing a quadcopter drone with a homemade communication protocol for control commands.

I am experiencing trouble with its range. It is on the 433 MHz band with a HC-12 used on both ends. 

That should get a good range, but I'm only getting like 100 meters if I'm lucky. I am trying to find out why. 

I just ran a test in which I monitored the 433 MHz band on a RTL-SDR with the drone's motors running idle and not running idle, in the vicinity. Below are the results. Can you give me your opinion on what is happening here, what the problem is, and what I can do to fix it?

[COPY + PASTE TEST RESULTS FROM ABOVE]
```

- [Claude Sonnet 4.5 Extended response](https://claude.ai/share/86e45d70-5896-49d8-a60c-27ac2298a760)
- [Copilot response](https://copilot.microsoft.com/shares/sniVMPKj119orcJuHz7rV)

## Solutions
- [These small ferrite beads](https://a.co/d/0iWIcgy0) are like resistors. Could be easy to use in on a perfboard!