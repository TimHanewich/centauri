![banner](https://i.imgur.com/oSwhZjR.png)

# Centauri: A Fully Custom Quadcopter System
*Centauri* is not just another drone project - it's a complete, end‑to‑end custom quadcopter ecosystem. From the airframe to the pilot's controller, from the communication platform to the analysis tools, every piece has been designed and built from scratch. At the heart of Centauri lies the  *Centauri Flight Controller*, a **custom MicroPython‑based flight controller** running efficiently on a low‑power Raspberry Pi Pico. Unlike most quadcopter projects that rely on off‑the‑shelf flight stacks, Centauri's controller is entirely original.

Centauri builds on my earlier [Scout flight controller](https://github.com/TimHanewich/scout), representing a major leap forward in capability, performance, and system integration.

To watch *Centauri* in action, click below:  
[![demo video](https://i.imgur.com/zbcKlFx.png)](https://www.youtube.com/watch?v=-Kj5vSNrLSk)

---

## What This Project Contains
![anatomy](https://i.imgur.com/6TYY0Nv.png)

This repository provides *everything* you need to build your own Centauri quadcopter and take flight. The system includes:

- **Centauri Quadcopter** — 3D‑printable frame design files, custom flight controller software, and wiring diagrams  
- **Pilot Controller** — a PC‑based program that reads input from a wired Xbox controller and transmits commands to the quadcopter  
  - **Bi‑directional Transceiver** — a USB‑connected platform with an HC‑12 radio module, enabling wireless communication between the PC and the drone  
- **Analysis Script** — a lightweight Python tool for unpacking binary telemetry logs stored on the Pico into human‑readable `.csv` files  

---

Centauri is a rare example of a quadcopter project where *every layer of the stack* (hardware, software, and communication) has been custom‑engineered.
