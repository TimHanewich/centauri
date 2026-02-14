# Tests to Perform
- Tests with props off... just quick check if it can get telemetry at all
    - *Did this, worked perfectly, even in other bedrooms*
- Was it just a loose u.fl connection? Or the u.fl connector is not properly connected to the rest (i.e. broken)? Check!
    - *I checked later that evening when deconstructing it due to the burnout. Appears to be connected well.*
- Strap it down with props on. Run it at 60% throttle in another room. This is a high-current load test. See if it works. (same pigtail)
    - *I did this at 60%, 80%, and then 100% throttle. Totally response to Rx at any throttle, even with props on (under load) in other bedrooms.*
- Still not working? **See if it was the POSITION of the antenna**: bring it lower (remove the mast). Put it where it was before. Do same test as above.
    - *Not needed: in the test above, it worked beautifully even in the mast position*
- Still not working? **See if it is the u.fl to SMA connector**: replace with the old 6 inch one.
    - *Not needed: in the test above, it worked beautifully even with the new 12-inch u.fl to SMA*
 
## Testing at Home
I brought it home, took props off, tried testing it here.

It did very well. With the antenna on the mast, laying on its side. I put it in several rooms away and would throttle up, then down, then up, then down. Never missed a beat. I then fastened the antenna mast back in the right position. Still did very well.

So what gives? This is *possibly* because there is no load on the motors and thus a minimal amount of current is going through them. But when there is **a lot of current** (during takeoff), that is when the EMI gets too strong and "chokes up" the HC-12 receiving antenna/pigtail.

## Props-On Tethered Punch Out (High Current) Tests on February 13, 2026
Following the [this 99% anamoly](https://youtu.be/4SKdvdp2M-Y?t=422), I performed a test in which I zip-tied down the drone to something heavy to hold it down, with props on (to ensure there is a load and a lot of current being drawn).

I did this to see if there was an issue the drone has in *receiving* new command data while in heavy load. (i.e. does the noise become so great that it can't get a "lower throttle!" update).

Here are the telemetry logs from that test:
- [Raw Log]()

There was absolutely no problem. I had the transmitter in my office and the drone in my bedroom, further than it was in the anomaly mentioned above. I had the max at 60% throttle, then 80%, then 100%. All with PID values on! Not once did it "choke up" and not be able to receive more telemetry. Even when punching out 100% continuously for seconds. From an Rx perspective, it seems to have passed with flying colors....

I did this for a few minutes. It did quite well. But because of how much current was passing through the leads, it did eventually melt. Photos [here](https://imgur.com/a/usOLZZ0).

So I'm somewhat bewildered in what happened today at the park. Bizarre how it glitched to 99% and then didn't receive input for several seconds. Could it have been a hiccup on the transmitter side? Doubt it...