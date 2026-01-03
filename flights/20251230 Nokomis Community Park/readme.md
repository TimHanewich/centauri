# Flying at Nokomis Community Park on December 30, 2025

![flights](https://i.imgur.com/FbECRNq.png)

- First flight using the new cloverleaf AIO module: [Wolfwhoop WT03](https://a.co/d/japxwkX)
- It was a cold day and a lot of wind coming from the north (Google shows 15 mph from the north)
- It felt awful - at even moderate range, like 30 meters away, I could tell some commands were not getting to it. It would comply, then not comply, then comply... definitely some packets are not being received.
- Before flying, I did a range test of the new cloverleaf antenna. 
    - I left the quad, turned on, on the bench (not armed). Walked off into the field. Got about 90 meters out of it, still quite solid with minimal static: https://i.imgur.com/yYzF3p3.png
    - But for some reason when *flying* not as good range. Better than the last AIO I was using for sure (the one without the antenna), but gets mildly staticy at like 40 meters.
        - **MAYBE THIS IS THE REASON**: according to AI, because this was my first fliht with the new cloverleaf antenna, I am not use to a strong antenna cranking out a signal. That signal could interfere with the HC-12.
    - **The first 7 seconds of the onboard video is me recording on the FPV monitor at that range just to show it!**. The last few seconds of it recording I begin walking back towards.

## Videos
- [Ground perspective (recorded on GoPro)](https://youtu.be/TPSHuW9jbeE) - *raw, concatenated*
- [Onboard Video](https://youtu.be/AnBjH0N_Z58) - *raw, concatenated (left at variable frame rate)*
    - Used command `ffmpeg -f concat -i files.txt -c copy all.avi` to concatenate
    - Also backed up raw on github here (no compression!): [onboard.avi](https://github.com/TimHanewich/centauri/releases/download/20/onboard.avi)
    - Important timestamps
        - 0:00 to 0:07 - testing new VTX AIO far away (recording at about 90 meters out - looks great!)
        - 1:03 to 1:10 - video feed looked great but control connection was not reaching. Packets were for sure dropping, but I fought it back.
        - 6:10 - *this appears like I lost connection but I don't think I did at this point from memory... just my bad flying I believe*
        - 6:20 - video feed looks great still, but control feed drops connection. Crashes. First impact to cloverleaf antenna. Cloverleaf is bent but still works. I bend it back and it works well again after.
        - 8:48 - video feed looks great still, but control feed drops connection. Crashes. Topples over. This snapps cloverleaf antenna at the base. It cuts in and out while still on the ground (I left it recording). Regains connection when I am very close (should have regained gradually). Cloverleaf antenna is now broken.
        - 8:50 - despite being flipped, the motors are still running. I remember hearing one of the motors screaming for a second or two before either it received "disarm" command or timed out (2 second failsafe if no telemetry received)
        - 10:10 - command link is going well but the cloverleaf antenna goes from great video to cutting out abruptly. I was using the FPV monitor to fly, so I crash. The gopro footage appears to confirm this - the crash was caused by me letting off the throttle because I lost FPV feed, not command link dropping.
        - 11:16 - this crash is caused by the props getting caught on the battery. Not radio related. But I think this may have jostled the AIO around further, possibly breaking it further.
        - 11:52 - I actually don't remember what happens here. I know it crashed and broke its rear right arm, but not sure how. Video feeds cuts out, but I'd be surprised if I was flying on the monitor here since I was just lifting off the ground. Maybe it also lost command control feed? anyway, it impacted the ground and broke the rear right arm.
- [The onboard video, but first upscaled to 2k with ffmpeg so youtube does not compress it so badly](https://youtu.be/sO8H_UmjUlE)

## Files
- [Raw telemetry log](https://github.com/TimHanewich/centauri/releases/download/20/log)
- [Telemetry log, unpacked as .csv file](https://github.com/TimHanewich/centauri/releases/download/20/log.csv)
- [Telemetry log as .xlsx, with notes on flights](https://github.com/TimHanewich/centauri/releases/download/20/log.xlsx)
- [Pictures from the day](https://imgur.com/a/0CBYwoW)
    - [This](https://i.imgur.com/g3udS8a.jpeg) was the position of the HC-12's spring antenna that day. Maybe this position had something to do with the poor command range.

## Battery
I only used a single battery as the quadcopter broke an arm before I had a chance to use the second battery. The battery I used was flown down to 15.4v and consumed 1,505 mAh (that is what it absorbed while charging after).