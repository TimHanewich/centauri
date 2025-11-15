## Future Improvements to Make
- Physical design
    - Clean up wires
    - Female plug for battery needs to be pulled in closer
    - Fix orientation of holes on arm so wires face ESC directly
    - "Slot" (holder) for ESCs on each arm
    - A better way to secure the battery
    - Option to use LiIon batteries instead (18650 or 21700)
- Software
    - Detailed telemetry recording to local storage
    - Minimize ongoing telemetry screening?

## Test Flight Videos
- [October 26, 2025: First Test Flight](https://x.com/TimHanewich/status/1982566777273163850)
- [November 2, 2025: First Outside Test Flight](https://youtu.be/w3_uWFIpgT4)
- [November 2, 2025: Test Flight 2](https://youtu.be/zN169FlOvNk)
    - [Uncut](https://youtu.be/7-dGYEiDu1g)
    - [Original video](https://youtu.be/cSAsppQKgEw) (no telemetry overlay)
    - [3rd Person View](https://youtube.com/shorts/7_4GXuOroN4)
    - [Drone view with 3rd person view](https://youtu.be/-Kj5vSNrLSk)

## Notable Commits
- `b1a1ab5dbd9689bbb8738018d4c9fa073f36ae01` - last commit with asynchronous design for LL-MCU before going to a single, synchronous loop
- `0420e1bebf144f58caa77302acc31632fdf95362` - last commit on LL-MCU before converting to integer math for PID loops (this is still float math, which has a memory leak)
- `ef7a0a76ea731c0cf48fcec6653566df2ed101c4` - last commit before moving to a single MCU architecture on the quadcopter and removing many of the sensors (focusing just on rate mode moving forward, abandoning plans for angle mode for now)
- `fffb3ff3d44cfcaa7561e7b6fd52661ec379cb79` - first successful flight on October 26, 2025
- `659b1df36c1548b4aa942828f4455192aad7f1b1` - final commit before removing calculation of pitch and roll angles (focus on just rates only)
- `f5d5ee41b780a90d643e48387e8cea1f385519a7` - final commit before introducing new HC-12 rx method *and* changing calculation of mean_pwm to avoid big ints
- `273427cc2d9437f5790862fe962c95087a1ab306` - final commit before introducing calculation of pitch and roll angles again (this time, more efficiently) and also raising the gyro and accelerometer full scale range.