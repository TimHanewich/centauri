![banner](https://i.imgur.com/0WhL6Q5.png)

# Centauri: A Fully Custom Quadcopter System
*Centauri* is a complete, end‑to‑end custom quadcopter system. From the airframe to the pilot's controller, from the communication platform to the analysis tools, every piece has been designed and built from scratch. At the heart of Centauri lies the *Centauri Flight Controller*, a **custom MicroPython‑based flight controller**, running efficiently on a low‑power Raspberry Pi Pico. Unlike most quadcopter projects that rely on off‑the‑shelf flight controllers, Centauri is entirely original.

Centauri builds on my earlier [Scout flight controller](https://github.com/TimHanewich/scout), representing a major leap forward in capability, performance, and system integration.

![preview_gif](https://i.imgur.com/mqoN9kG.gif)

To watch *Centauri* in action, click below:  
[![demo video](https://i.imgur.com/zbcKlFx.png)](https://www.youtube.com/watch?v=-Kj5vSNrLSk)

## In This Project
![anatomy](https://i.imgur.com/6TYY0Nv.png)

This repository provides *everything* you need to build your own Centauri quadcopter and take flight. This includes:

|Project Component|Thumbnail|Description|
|-|-|-|
|[Quadcopter](./components/quadcopter/)|![img](https://i.imgur.com/yLjl0wW.png)|Custom quadcopter, with:<br>- [3D-Printable Design](https://www.thingiverse.com/thing:7194383)<br>- [Components List](./components/quadcopter/)<br>- [Wiring Diagram](https://app.diagrams.net/#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FTimHanewich%2Fcentauri%2Frefs%2Fheads%2Fmaster%2Fcomponents%2Fquadcopter%2Fwiring.drawio#%7B%22pageId%22%3A%22W1gebfnubh0FSxZTr-fW%22%7D)<br>- [Custom Flight Controller, written in MicroPython](https://github.com/TimHanewich/centauri/blob/master/components/quadcopter/src/main.py)|
|[Transmitter](./components/transmitter/)|![img](https://i.imgur.com/k71XDjl.png)|Serves as pilot's interface for controlling the quadcopter. Includes:<br>- [Main Python program for a PC](./components/transmitter/src/PC/)<br>- [USB Radio Transceiver Platform](./components/transmitter/readme.md#transceiver-platform)<br>- Custom binary communication protocol|
|[Analysis Script](./components/analysis/)|![img](https://i.imgur.com/AcsRmQh.png)|Lightweight Python tool for unpacking binary telemetry logs stored on the quadcopter's MCU into human‑readable `.csv` files|