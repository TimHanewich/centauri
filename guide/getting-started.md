# Building the Centauri Flight Controller, Chapter 1: Introduction
[Centauri](https://github.com/TimHanewich/Centauri) is a custom quadcopter flight controller, written in Python, and developed for low-cost, low-powered microcontrollers like the Rasperry Pi Pico.

This chapter will be the first in a series describing how I developed the Centauri flight controller and its peripheral supporting systems step by step! You can follow along in this guide while *you* build Centauri yourself (I provide everything that is needed!) or use this to glean important information for other engineering projects.

But first, before we begin, some education about how quadcopters fly...

## What is a Flight Controller?
A quadcopter's flight controller is a system that allows the quadcopter to achieve stable flight. The flight controller does several things, but its primary purpose is to ensure the drone's rate of change in its three axes - pitch, roll, and yaw - is matching the pilot's *desired* rate of change in those three axes. 

While quadcopter flight controllers have become more and more common with the rise of DJI and other drone manufacturers, they're nothing short of amazing in what they do. Later in this guide you'll learn more about how incredile they are.

## Components Needed
While I refer to the quadcopter I've developed myself as *Centauri*, it is important to note that this entire project is not *only* the flight controller software that lives on the quadcopter's microcontroller unit (MCU). Really, this project contains three separate groupings of resources:
- **Centauri**: the quadcopter's 3D design files and flight controller code
- **The Controller**: a Python-based program that runs on second device (Windows/Linux computer) and continuously transmits control input commands to the Centauri quadcopter, along with a transceiver that allows bidirectional communication with the quadcopter

### Components needed to build the Centauri Quadcopter:
![pic of the quadcopter]()
- XXX grams of PLA for the 3D-printed body (assuming 30% infill)
- 4 30mm M3 screws
- 4 brushless motors - *I use [these Readytosky 2300KV motors](https://a.co/d/6Pua6ZV)*
- 4 5-inch propellers - *I use [these 3-blade propellers](https://a.co/d/6pNksCt)
- 4 brushless Electronic Speed Controllers (ESCs) - I use [this four pack](https://a.co/d/6Rvq71s)
- 1 Raspberry Pi Pico to serve as the MCU
- 1 HC-12 Radio Communication Module
- 1 MPU-6050 accelerometer/gyroscope
- 1 LM2596 buck converter set to 5V
- **RESISTORS FOR VOLTAGE DIVIDER**
- Some wire (I use 22 gauge)

### Components needed for the Controller:
![pic of PC with transceiver]()

You will need:
- A Windows/Linux PC
- An Xbox controller
- A USB cable to plug the Xbox controller into the PC
- XXX grams of PLA for the 3D-printed transceiver platform
- 1 [CP2102 USB to UART module](https://a.co/d/4rJMLjy)
- 1 Raspberry Pi Pico
- 1 HC-12 Radio Communication Module
- Some wire (I use 22 gauge)

