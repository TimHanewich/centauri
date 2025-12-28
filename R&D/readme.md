## Pre-Flight Packing List
- Quadcopter
- FPV Monitor
- Spare phone battery for charging FPV monitor (w/ micro USB cable!)
- Laptop
- Transceiver platform
- Xbox controller w/ USB C cable
- 3D-printed phone holder (to place FPV monitor in)
- Two charged 4S LiPo batteries
- Blue tape
- Pliers
- M3 allen wrench (for mount screw)
- Wrench (for taking off/on propellers)
- Hat & Gloves
- GoPro?
    - GoPro
    - Charged GoPro batteries
    - Tripod

## Future Improvements to Make
- Physical design
    - Antenna position!
        - Maybe this one: https://a.co/d/hyoroY7
        - Or Maybe this one: https://www.amazon.com/dp/B0C1FCZM94
    - Clean up wires
    - Female plug for battery needs to be pulled in closer
    - Fix orientation of holes on arm so wires face ESC directly
    - "Slot" (holder) for ESCs on each arm
    - A better way to secure the battery
    - Option to use LiIon batteries instead (18650 or 21700)
- Software
    - Reduce baudrate of telemetry to make it more resilient?
    - "Dump telemetry log" command to delete onboard telemetry + restart
    - Detailed telemetry recording to local storage
    - Minimize ongoing telemetry screening?
    - Increase telemetry buffer size to allow for longer flights

## Notable Commits
- `b1a1ab5dbd9689bbb8738018d4c9fa073f36ae01` - last commit with asynchronous design for LL-MCU before going to a single, synchronous loop
- `0420e1bebf144f58caa77302acc31632fdf95362` - last commit on LL-MCU before converting to integer math for PID loops (this is still float math, which has a memory leak)
- `ef7a0a76ea731c0cf48fcec6653566df2ed101c4` - last commit before moving to a single MCU architecture on the quadcopter and removing many of the sensors (focusing just on rate mode moving forward, abandoning plans for angle mode for now)
- `fffb3ff3d44cfcaa7561e7b6fd52661ec379cb79` - first successful flight on October 26, 2025
- `659b1df36c1548b4aa942828f4455192aad7f1b1` - final commit before removing calculation of pitch and roll angles (focus on just rates only)
- `f5d5ee41b780a90d643e48387e8cea1f385519a7` - final commit before introducing new HC-12 rx method *and* changing calculation of mean_pwm to avoid big ints
- `273427cc2d9437f5790862fe962c95087a1ab306` - final commit before introducing calculation of pitch and roll angles again (this time, more efficiently) and also raising the gyro and accelerometer full scale range.
- `fbd5de0de2cc9d7a86db661d32e3ee9e1b32a7ba` - final commit before the handheld RPi converts to event-driven telemetry (away from regular packet-driven)
- `0e39ab9c6f7535b9b8dad39d55be70867498bd2e` - final commit before the handheld RPi converts BACK to snapshot-driven telemetry
- `441092dd6d612117bf2bb693eeb86aabf4128330` - final commit that contains the handheld transmitter code and data (later removed due to giving up on this effort for now)

## Misc. Tips
- [How to concatenate video with ffmpeg](https://copilot.microsoft.com/shares/KxoXheL2Kgo7QkC75ZyW9)