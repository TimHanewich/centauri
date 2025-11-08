# The "Centauri" Quadcopter
This page contains everything you need to fully reconstruct the Centauri quadcopter exactly as you've seen in the demo videos!

## Components Needed


## 3D Printed Body
![body](https://i.imgur.com/kmZ4yZn.gif)

You can download the `.stl` files to 3D print the quadcopter body [from Thingiverse here](https://www.thingiverse.com/thing:7194383).

The Centauri frame is designed to balance simplicity and strength. Its 3D‑printed design is lightweight yet durable, making assembly straightforward without sacrificing structural integrity. With a 225 mm diagonal motor‑to‑motor distance, the frame supports 5‑inch propellers, offering an ideal setup for stable flight and responsive performance.

To print all components at 30% infill, 149 grams of PLA are required, as shown below:

|Part|PLA @ 30% Infill|
|-|-|
|Level 1|30 g|
|Level 2|30 g|
|4 Arms|68 g|
|MPU-6050 Frame|4 g|
|LM5696 Frame|9 g|
|GoPro Mount|8 g|

If you'd like to customize or experiment with the design, you can download a folder containing all the iterative saves that led to the final Centauri frame. These snapshots make it easier to trace back to an earlier, less‑modified version of a part and adapt it to your needs:
- [August 10, 2025 – original Centauri quadcopter design with two MCUs](https://github.com/TimHanewich/centauri/releases/download/1/design.zip)
- [September 17, 2025 – streamlined Centauri design with a single MCU (Pico), sensors removed, and zip‑tie slots added for securing the battery adapter](https://github.com/TimHanewich/centauri/releases/download/3/centauri-mono.zip)

## Wiring Diagram

## Flight Controller Firmware