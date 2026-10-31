# The Centauri Quadcopter
![quadcopter](https://i.imgur.com/EvqdOPa.jpeg)

The Centauri quadcopter was completely designed and developed from the ground up: the 3D-printed body, the electronics package, *and* the quadcopter flight controller firmware!

This page contains everything you need to fully reconstruct the Centauri quadcopter exactly as you've seen in the demo videos.

## Parts List
At the heart of the Centauri quadcopter is the *Centauri Flight Controller Carrier Board*. This is a lightweight PCB that handles all electrical connections between the systems for you, allowing you to focus on the build instead of fighting a wire rats nest!

![pcb](https://i.imgur.com/3tIb9Us.png)

To purchase the PCB directly, visit [fullstackflight.com/shop](https://fullstackflight.com/shop/)!

For a full list of the remaining components needed to build *Centauri*, visit [fullstackflight.com/parts](https://fullstackflight.com/parts).

## 3D Printed Body
![body](https://i.imgur.com/GHmXqp6.gif)

The Centauri frame is designed to balance simplicity and strength. Its 3D‑printed design is lightweight yet durable, making assembly straightforward without sacrificing structural integrity. With a 225 mm diagonal motor‑to‑motor distance, the frame supports 5‑inch propellers, offering an ideal setup for stable flight and responsive performance.

You can download the `.stl` files to 3D print the quadcopter body [from Thingiverse here](https://www.thingiverse.com/thing:7429193).

30% infill is recommended for printing, which will use approximately **155 grams** of PLA, shown below.

|Part|Grams of PLA @ 30% Infill|
|-|-|
|Level 1|30 g|
|Level 2|30 g|
|4 Arms|69 g|
|MPU-6050 Frame|3 g|
|GoPro Mount|8 g|
|Antenna Mast (3 components)|15 g|

## Flight Controller Firmware
The Centauri Flight Controller firmware is written in MicroPython and is designed (at least to the best of my ability), to run as efficiently as possible, but within legibility reason.

The flight controller code can be found [here](./src/).

With your quadcopter fully assembled and wired up, all you need to do is flash these files to the root directory of the Raspberry Pi Pico acting as the MCU. Assuming you wired each component to the Pico's GP pins as depicted in the wiring diagram, it will work without further configuration. Alternatively, you may need to make minor tweaks to the pin mappings.

## ESC Calibration Script
I'm also providing a lightweight script to calibrate brand new ESCs, available in [/calibrate](./calibrate/).

## FPV Flying
You can also fly Centauri as an FPV quadcopter just by fastening a FPV camera/VTX/antenna to it! This is optional and not required to achieve flight, but if you want to fly via FPV goggles (or monitor), you should do this!

I purchased and had a lot of success with the [AKK BA3](https://amzn.to/4yjdSJW) FPV All-in-One module. If you decide to use this in your quadcopter, you can use [this 3D-printed frame](https://www.thingiverse.com/thing:7229291) I designed for it to securely hold it in place on your quadcopter, mounted at the front. Print `prong_base.stl` and `akk_ba3_mount_v2.stl`.

![v2](https://i.imgur.com/JVTK1yY.jpeg)

## Weight

### Individual Components
- The 4S 3,300 mAh LiPo battery I use is 347 grams.
- GoPro, GoPro frame, and M4 screw + nut for attaching: [146 grams](https://i.imgur.com/HSME9m7.jpeg)

### Centauri Quadcopter V1
- In "Configuration D" (antenna mast) with FPV camera attached: [824 grams](https://i.imgur.com/GGvb2es.jpeg)

### Centauri Quadcopter V2
- In "Configuration D" (antenna mast) with FPV camera attached: [782 grams](https://i.imgur.com/Kh0mNKz.jpeg)