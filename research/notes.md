## Testing Notes on Oct 24, 2025
- Pitch PID doesnt seem right - is it reversed? Doesnt seem to be resisting. Is it inverted? May be doing the opposite
- Roll feels quite good. Got this far with P and I, didn't get to D yet:
    - Idle throttle = 8%
    - Max throttle = 25%
    - Roll kP: 15,000
    - Roll kI: 3,500
    - Roll kD: 0
    - All else set to 0 (isolte testing of roll axis)
    - I limit = 25,0000. May be safe to bring this higher, I feel it spoolign safely and slowly.