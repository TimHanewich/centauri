## A Good PID Ratio
Provided by [this Copilot chat](https://copilot.microsoft.com/shares/dZewrk4FBsUZGGAGu6Wxs) (it includes angle loops too):
- P
- I = 10-30% of P
- D = 5-20% of P

## Steps to PID Tuning:
Provided by [this chat](https://copilot.microsoft.com/shares/dZewrk4FBsUZGGAGu6Wxs), below:

1. Safety First
- **Test environment:** Open space, soft ground if possible.
- **Throttle limit:** Use a low throttle cap or tether for first hover attempts.
- **Monitor temps:** Motors and ESCs can overheat if gains are too high.

---

2. Start with P Only
- Set **I = 0, D = 0**.
- Increase **P** gradually (roll/pitch together, yaw separately).
- Watch behavior:
  - Too low → quad won’t self‑level, feels mushy.
  - Just right → resists disturbances, feels crisp.
  - Too high → fast oscillations (“shaking”).
- Back off slightly from the onset of oscillation.

---

3. Add I for Holding Power
- With P stable, introduce **I** slowly.
- Purpose: corrects long‑term drift (wind, motor imbalance).
- Signs:
  - Too low → quad drifts off when sticks are released.
  - Just right → holds attitude steadily.
  - Too high → slow “wobble” or sluggish bounce after inputs.
- Clamp the integral term to prevent runaway.

---

4. Introduce D for Damping
- Add a small **D** to reduce overshoot and bounce‑back.
- Signs:
  - Too low → overshoot, “bouncy” stops.
  - Just right → smooth, precise stops.
  - Too high → noisy motors, twitchiness, hot ESCs.
- Consider filtering gyro or D term if noise is an issue.

---

5. Tune Each Axis
- **Roll and pitch:** usually tuned together (similar dynamics).
- **Yaw:** often needs different gains (lower P, higher I, little or no D).

---

6. Iterate
- Revisit **P** after adding I and D — they interact.
- Make small adjustments rather than big jumps.
- Test progression:
  1. Hover
  2. Forward flight
  3. Aggressive maneuvers

---

7. Practical Shortcuts
- Many flight stacks (Betaflight, PX4, ArduPilot) publish “starter” PID values for common frame sizes.
- Blackbox logging or gyro traces help visualize oscillations and overshoot.

---

✅ Summary
1. Raise **P** until oscillation, then back off.  
2. Add **I** until it holds attitude.  
3. Add **D** to smooth and damp.  
4. Iterate per axis.

## Excellent Rigs for PID Tuning (Safely) from Scratch
- https://www.youtube.com/shorts/4T9lB4C46Tk - SIMPLE BUT EFFECTIVE
- https://www.youtube.com/watch?v=dMRDzicSvXk
- https://www.youtube.com/shorts/NGpEHnExb2U
- https://www.youtube.com/shorts/3mdGhCtTlcQ
- https://www.youtube.com/shorts/VSAUrrOmbZw
- https://www.youtube.com/shorts/5itLYbTa7eU
- https://www.youtube.com/watch?v=M09hvlPbqek
- https://www.youtube.com/watch?v=EkgV_cxCnU4
- https://www.youtube.com/watch?v=aZnTlzgtG2Q