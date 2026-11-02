# Link
Centauri *Link* is a small, lightweight, handheld device for monitoring the radio communications between the Pilot's transmitter (their "controller" used to control the drone) and the drone itself ("quadcopter"). It is used for observability into the communication, often as a diagnostic device. 

![link](https://i.imgur.com/zCiTALG.png)

## Why Build *Link*?
It is highly recommended that you build and use *Link* prior to testing your drone at distance to verify the approximate range you can safely fly within without losing connection. If you fly outside of the maximum range of the transmitter, it will be a potentially catastrophic crash! *Link* allows you to simply walk to the end of a field until you no longer receive reception - and then you know how far you can fly!

![walking with it](https://i.imgur.com/JYjIqjU.gif)

## Assembling Link
![assembly process](https://i.imgur.com/xFjqYGj.png)

You can assemble your own *Link* handheld device! Follow the steps below:
1. Purchase the *Link Carrier Board* from [Full Stack Flight's Shop](https://fullstackflight.com/shop/#link-carrier-board).
2. Purchase necessary parts from [the parts list](https://fullstackflight.com/parts/#link).
3. 3D-Print the enclosure - design files [here on Thingiverse](https://www.thingiverse.com/thing:7429960/files).
4. Wire it up!

### 3D-Printing Notes
There are a total of three pieces involved in the 3D-printed enclosure for *Link*, detailed below:
|Part|Description|Grams of PLA at 30% infill|
|-|-|-|
|`top.stl`|The top plate cover of the enclosure. Houses the OLED screen, power switch, and bush button.|14 g|
|`bottom.stl`|The main housing enclosure for most components. Houses the charge controller, battery, Carrier Board, and all other components mounted to the board.|54 g|
|`18650_frame.stl`|A frame for holding the 18650 battery that is used as the power source within the enclosure|10 g|

### Wiring Notes
Wiring up *Link* is rather straightforward: all electrical components involved are either directly soldered to the Carrier Board itself, and if not, directly wired up to drill holes in the Carrier Board where the necessary electrical connections are handled by the board.

Take the pic below, for example. This is a nearly-completed build of *Link*. The only missing component here is the 18650 battery (in its frame), which will be housed in the empty space within the enclosure. The battery's leads (wrapped wire around the frame ends) will be directly connected to the `BAT1` drill holes on the Carrier Board (bottom left corner of the board, near the "CENTAURI" logo).

![pic](https://i.imgur.com/ycl3nsC.jpeg)