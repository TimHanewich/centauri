# The Centauri Quadcopter
![quadcopter](https://i.imgur.com/8PIMXgb.jpeg)

The Centauri quadcopter was completely designed and developed from the ground up - the 3D-printed body, the electronics package, *and* the quadcopter flight controller firmware!

This page contains everything you need to fully reconstruct the Centauri quadcopter exactly as you've seen in the demo videos.

## Components Needed
Here you'll find a list of all the components need to fabricate and assemble your own Centauri quadcopter. In the components list below, I provide estimates for the prices for each component, normally just using the price that *I* paid for the component, along with that component link provided.

|Component|Est. Price (USD)|
|-|-|
|PLA for 3D Printing the Frame|$2.25|
|[4 Brushless Motors](https://a.co/d/6Pua6ZV)|$38.99|
|[4 Propellers (2 CW, 2 CWW)](https://a.co/d/6pNksCt)|$4.40|
|[4 Electronic Speed Controllers (ESCs)](https://a.co/d/jm61OU4)|$31.29|
|[MPU-6050 IMU](https://a.co/d/429WnGv)|$3.67|
|[HC-12](https://a.co/d/8L9nex9)|$9.49|
|[4S LiPo Battery](https://a.co/d/f8O8tPR)|$32.29|
|100,000 Ohm Resistor|$0.05|
|22,000 Ohm Resistor|$0.05|
|[LM2596 Buck Converter](https://a.co/d/f8O8tPR)|$1.30|
|Raspberry Pi Pico|$4.00|
|Misc. Screws and Nuts|$2.00|
|Misc. Wire|$2.00|

All in, the estimate in cost is approximately **$132 USD** - at least if you use parts I did above! You are welcome to experiment with different motors, propellers, ESCs, a smaller battery, etc.!


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
![wiring](https://i.imgur.com/8pOK9ik.png)

With all the components assembled on the 3D-printed frame, you are now ready to wire everything up! The wiring diagram is depicted above, but you can also [download it as a SVG](https://github.com/TimHanewich/centauri/releases/download/13/wiring.drawio.svg) or open [the original design directly in draw.io](https://app.diagrams.net/#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FTimHanewich%2Fcentauri%2Frefs%2Fheads%2Fmaster%2Fcomponents%2Fquadcopter%2Fwiring.drawio#%7B%22pageId%22%3A%22W1gebfnubh0FSxZTr-fW%22%7D).

## Flight Controller Firmware
The Centauri Flight Controller firmware is written in MicroPython and is designed (at least to the best of my ability), to run as efficiently as possible, but within legibility reason.

The flight controller code can be found [here](./src/). It is only two `.py` files:
- `main.py` - the main flight controller program that receives pilot input over a radio channel, observes IMU readings, and applies thrust to reconcile actual gyroscopic rates with desired rates.
- `tools.py` - contains helper functions for unpacking command input, packing telemetry data, and more.

With your quadcopter fully assembled and wired up, all you need to do is flash these two files to the root directory of the Raspberry Pi Pico acting as the MCU. Assuming you wired each component to the Pico's GP pins as depicted in the wiring diagram, it will work without further configuration. Alternatively, you may need to make minor tweaks to the pin mappings.

## Weight
- Fully assembled drone: 427 grams
- 4S LiPo 3,300 mAh battery: 347 grams
- GoPro, GoPro frame, and M4 screw + nut for attaching: [146 grams](https://i.imgur.com/HSME9m7.jpeg)
- **TOTAL, FULLY-LOADED WEIGHT: [920 grams](https://i.imgur.com/8M9BNGq.jpeg)**