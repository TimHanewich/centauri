![banner](https://i.imgur.com/77WjAKV.png)

![Stars](https://img.shields.io/github/stars/TimHanewich/centauri?style=social) ![Forks](https://img.shields.io/github/forks/TimHanewich/centauri?style=social) ![understandability](https://img.shields.io/badge/understandability-HIGH😄-blue) [![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-red?logo=github)](https://github.com/sponsors/TimHanewich)

# Centauri: A Fully Custom Quadcopter System
*Centauri* is a complete, end‑to‑end custom quadcopter system. From the airframe to the pilot's controller, from the communication platform to the analysis tools, every piece has been designed and built from scratch. At the heart of Centauri lies the *Centauri Flight Controller*, a **custom MicroPython‑based flight controller**, running efficiently on a low‑power Raspberry Pi Pico. Unlike most quadcopter projects that rely on off‑the‑shelf flight controllers, Centauri is entirely original.

Centauri builds on my earlier [Scout flight controller](https://github.com/TimHanewich/scout), representing a major leap forward in capability, performance, and system integration.

https://github.com/user-attachments/assets/0ff39eb4-ba65-41b6-8ec0-05878d19641e

To see how *Centauri* was made and watch it in action, click below:  
[![demo video](https://i.imgur.com/Hi0yzIR.png)](https://www.youtube.com/watch?v=4ocy2szvcbM)

## In This Project
This repository provides *everything* you need to build your own Centauri quadcopter and take flight. This includes:

![anatomy](https://i.imgur.com/3nwqHiE.png)

|Project Component|Thumbnail|Description|
|-|-|-|
|[Quadcopter](./components/quadcopter/)|![img](https://i.imgur.com/3xnsZLt.png)|Custom quadcopter, with:<br>- [3D-Printable Design](https://www.thingiverse.com/thing:7194383)<br>- [Components List](./components/quadcopter/)<br>- [Wiring Diagram](https://app.diagrams.net/#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FTimHanewich%2Fcentauri%2Frefs%2Fheads%2Fmaster%2Fcomponents%2Fquadcopter%2Fwiring.drawio#%7B%22pageId%22%3A%22W1gebfnubh0FSxZTr-fW%22%7D)<br>- [Custom Flight Controller, written in MicroPython](https://github.com/TimHanewich/centauri/blob/master/components/quadcopter/src/main.py)|
|[Transmitter](./components/transmitter/)|![img](https://i.imgur.com/dGlMm5V.png)|Serves as pilot's interface for controlling the quadcopter. Includes:<br>- [Main Python program for a PC](./components/transmitter/src/PC/)<br>- [USB Radio Transceiver Platform](./components/transmitter/readme.md#transceiver-platform)<br>- Custom binary communication protocol|
|[Telemetry Extracting](./components/analysis/)|![img](https://i.imgur.com/dSfSNne.png)|Python program for unpacking binary telemetry logs stored on the quadcopter's MCU into human‑readable `.csv` files|

## Article Series
Want the full story behind how Centauri was designed and built? Check out the *Full Stack Flight* article series:
- [Full-Stack Flight: Building a Quadcopter Ecosystem from Scratch](https://medium.com/@timhanewich/full-stack-flight-building-a-quadcopter-ecosystem-from-scratch-18d43386bb6d)
- [Full-Stack Flight, Chapter 1: The Centauri Ecosystem](https://medium.com/@timhanewich/full-stack-flight-chapter-1-the-centauri-ecosystem-eacfcecc90f5)
- [Full-Stack Flight, Chapter 2: Defining a Communication Protocol](https://medium.com/@timhanewich/full-stack-flight-chapter-2-defining-a-communication-protocol-41bfc589a319)
- [Full-Stack Flight, Chapter 3: Quadcopter, Part 1: Designing a 3D-Printed Airframe](https://medium.com/@timhanewich/full-stack-flight-chapter-3-quadcopter-part-1-designing-a-3d-printed-airframe-9d4f9021a68c)
- [Full-Stack Flight, Chapter 4: Quadcopter, Part 2: Hardware and Electronics Package](https://medium.com/@timhanewich/full-stack-flight-chapter-4-quadcopter-part-2-hardware-and-electronics-package-69a5c26bc30b)
- [Full-Stack Flight, Chapter 5: Quadcopter, Part 3: The Flight Controller](https://medium.com/@timhanewich/full-stack-flight-chapter-5-quadcopter-part-3-the-flight-controller-310b3f288975)
- [Full-Stack Flight, Chapter 6: Transmitter, Part 1: Transceiver Platform](https://medium.com/@timhanewich/full-stack-flight-chapter-6-transmitter-part-1-transceiver-platform-7aee3793da9a)
- [Full-Stack Flight, Chapter 7: Transmitter, Part 2: The Pilot's Control Interface](https://medium.com/@timhanewich/full-stack-flight-chapter-7-transmitter-part-2-the-pilots-control-interface-dd14b90d5169)
- [Full-Stack Flight, Chapter 8: Unpacking Flight Telemetry for Analysis](https://medium.com/@timhanewich/full-stack-flight-chapter-8-unpacking-flight-telemetry-for-analysis-73d251a4a449)
- [Full-Stack Flight, Chapter 9: Closing Thoughts](https://medium.com/@timhanewich/full-stack-flight-chapter-9-closing-thoughts-1f6855269e5f)

## Join the Discord
![join discord promo](https://i.imgur.com/NBVaQjr.png)

You can join our maker community by joining the **Full Stack Flight Discord Server**! This is a space for any makers interested in building their own*iteration of *Centauri* to share progress and ideas, ask questions, and celebrate their successes. Click [here](https://discord.gg/wwqfmCUzGg) to join!

## License
Copyright 2026 Tim Hanewich. This project is licensed under the GNU General Public License v3. See [license.md](./license.md) for details.