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

## Notable Commits
- `b1a1ab5dbd9689bbb8738018d4c9fa073f36ae01` - last commit with asynchronous design for LL-MCU before going to a single, synchronous loop
- `0420e1bebf144f58caa77302acc31632fdf95362` - last commit on LL-MCU before converting to integer math for PID loops (this is still float math, which has a memory leak)
- `ef7a0a76ea731c0cf48fcec6653566df2ed101c4` - last commit before moving to a single MCU architecture on the quadcopter and removing many of the sensors (focusing just on rate mode moving forward, abandoning plans for angle mode for now)
- `fffb3ff3d44cfcaa7561e7b6fd52661ec379cb79` - first successful flight on October 26, 2025