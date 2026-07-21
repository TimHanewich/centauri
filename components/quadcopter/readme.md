# The Centauri Quadcopter
![quadcopter](https://i.imgur.com/LfK57Q5.jpeg)

The Centauri quadcopter was completely designed and developed from the ground up - the 3D-printed body, the electronics package, *and* the quadcopter flight controller firmware!

This page contains everything you need to fully reconstruct the Centauri quadcopter exactly as you've seen in the demo videos.

## Components Needed
Here you'll find a list of all the components needed to fabricate and assemble your own Centauri quadcopter, along with the component link provided.

|Component|
|-|
|PLA for 3D Printing the Frame|
|[4 Brushless Motors](https://amzn.to/44lyILf)|
|[4 Propellers (2 CW, 2 CWW)](https://amzn.to/3QQwuAt)|
|[4 Electronic Speed Controllers (ESCs)](https://amzn.to/3SMnnBr)|
|[MPU-6050 IMU](https://amzn.to/4yh76Ev)|
|[HC-12](https://amzn.to/4eWx48V)|
|[TI.10.0111 433 MHz Antenna](https://www.digikey.com/en/products/detail/taoglas-limited/TI-10-0111/3131969)|
|[U.FL to SMA Coaxial Cable](https://amzn.to/4f92Hee)|
|[XT60 Connector](https://amzn.to/4vwD25n)|
|[4S LiPo Battery](https://amzn.to/3RwAqq7)|
|[100,000 Ohm Resistor and 22,000 Ohm Resistor](https://amzn.to/4aNJ0Yb)|
|[LM2596 Buck Converter](https://amzn.to/4vp6zh8)|
|1 [10 uf Capacitor](https://amzn.to/4bFcebU)|
|1 [0.1 uf Capacitor](https://amzn.to/44lKKUT)|
|2 [Ferrite Beads](https://amzn.to/3SVQRNa)|
|[Raspberry Pi Pico](https://amzn.to/4vZ5DkH)|
|Misc. Screws and Nuts|
|Misc. Wire|

You are welcome to experiment with different motors, propellers, ESCs, a smaller battery, etc.!


## 3D Printed Body
![body](https://i.imgur.com/SGcsq0V.gif)

You can download the `.stl` files to 3D print the quadcopter body [from Thingiverse here](https://www.thingiverse.com/thing:7194383).

The Centauri frame is designed to balance simplicity and strength. Its 3D‑printed design is lightweight yet durable, making assembly straightforward without sacrificing structural integrity. With a 225 mm diagonal motor‑to‑motor distance, the frame supports 5‑inch propellers, offering an ideal setup for stable flight and responsive performance.

To print all components at 30% infill, **164 grams** of PLA are required, as shown below:

|Part|PLA @ 30% Infill|
|-|-|
|Level 1|30 g|
|Level 2|30 g|
|4 Arms|68 g|
|MPU-6050 Frame|4 g|
|LM2596 Frame|9 g|
|GoPro Mount|8 g|
|Antenna Mast (3 components)|15 g|

If you'd like to customize or experiment with the design, you can download a folder containing all the iterative saves that led to the final Centauri frame. These snapshots make it easier to trace back to an earlier, less‑modified version of a part and adapt it to your needs:
- [August 10, 2025 – original Centauri quadcopter design with two MCUs](https://github.com/TimHanewich/centauri/releases/download/1/design.zip)
- [September 17, 2025 – streamlined Centauri design with a single MCU (Pico), sensors removed, and zip‑tie slots added for securing the battery adapter](https://github.com/TimHanewich/centauri/releases/download/3/centauri-mono.zip)
- [January 18, 2026 - designing the arm with a port for an SMA mount for an antenna](https://github.com/TimHanewich/centauri/releases/download/22/arm-antenna.zip)
- [February 7, 2026 - designed a new arm with a SMA port for an antenna on the OUTSIDE of the body (rear)](https://github.com/TimHanewich/centauri/releases/download/35/arm-antenna.zip)
- [February 12, 2026 - re-designed rear arm with port to instead mount a mast for the antenna to be at the top](https://github.com/TimHanewich/centauri/releases/download/44/arm-antenna.zip)

## Wiring Diagram
![wiring](https://i.imgur.com/0YmcytB.png)

With all the components assembled on the 3D-printed frame, you are now ready to wire everything up! The wiring diagram is depicted above, but you can also [download it as a SVG](https://github.com/TimHanewich/centauri/releases/download/13/wiring.drawio.svg) or open [the original design directly in draw.io](https://app.diagrams.net/#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FTimHanewich%2Fcentauri%2Frefs%2Fheads%2Fmaster%2Fcomponents%2Fquadcopter%2Fwiring.drawio#%7B%22pageId%22%3A%22W1gebfnubh0FSxZTr-fW%22%7D).

## Flight Controller Firmware
The Centauri Flight Controller firmware is written in MicroPython and is designed (at least to the best of my ability), to run as efficiently as possible, but within legibility reason.

The flight controller code can be found [here](./src/). It is only two `.py` files:
- `main.py` - the main flight controller program that receives pilot input over a radio channel, observes IMU readings, and applies thrust to reconcile actual gyroscopic rates with desired rates.
- `tools.py` - contains helper functions for unpacking command input, packing telemetry data, and more.

With your quadcopter fully assembled and wired up, all you need to do is flash these two files to the root directory of the Raspberry Pi Pico acting as the MCU. Assuming you wired each component to the Pico's GP pins as depicted in the wiring diagram, it will work without further configuration. Alternatively, you may need to make minor tweaks to the pin mappings.

## Weight
- Component weights
    - Quadcopter fully assembled, without battery, FPV camera, or GoPro: 427 grams
    - The 4S 3,300 mAh LiPo battery I use is 347 grams.
- Asembled Operating Weights
    - By itself, with 4S battery: ~774 grams
    - With FPV camera attached: [790 grams](https://i.imgur.com/AakQhmH.jpeg)
    - With GoPro attached: [920 grams](https://i.imgur.com/8M9BNGq.jpeg)
        - GoPro, GoPro frame, and M4 screw + nut for attaching: [146 grams](https://i.imgur.com/HSME9m7.jpeg)
    - In "Configuration D" (antenna mast) with FPV camera attached: [824 grams](https://i.imgur.com/GGvb2es.jpeg)

## FPV Flying
You can also fly Centauri as an FPV quadcopter just by fastening a FPV camera/VTX/antenna to it! I did this, read more about it [here](./FPV/)!

## ESC Calibration Script
I'm also providing a lightweight script to calibrate brand new ESCs, available in [/calibrate](./calibrate/).