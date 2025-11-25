# Video Series


- **Chapter 1**: Introduction
    - The components
    - How the data flows
- Then dive into each component more:
    - **Chapter 2: The Controller**
        - Uses pygame to get xbox controller input
        - Uses rich to show the display
        - Uses async to do everything at once
        - Reads input from pygame, min/maxs it with the min/max throttle
        - Uses tools.py to pack into a data packet
        - Uses pyserial to send data to transceiver platform, which then sends it to the quadcopter
        - The pyserial program passes along everything except TIMHPONG.
        - The transceiver also receives data coming in from quadcopter. Telemetry data.
        - Telemetry data shown in the pilot control.
        - Not just used for control input. Also used for settings flashing!
    - **Chapter 3: The Quadcopter**
    - **Chapter 4: The Analysis Script**

## Short showing Development
- **August 1** - [Drone design](https://x.com/TimHanewich/status/1953264219979153733/photo/1)
- **August 3** - [Controller program](https://x.com/TimHanewich/status/1952076309426782209/video/1)
- **August 7** - 3D print begins (video of printing level1 + [3D printed arms pic](https://i.imgur.com/d4BYgrN.jpeg))
- **August 8** - begin assembling on level 1 picture
- **August ?** - [Communication Protocol developed](https://app.diagrams.net/#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FTimHanewich%2Fcentauri%2Frefs%2Fheads%2Fmaster%2FR%2526D%2Fcommunication%2Fcommunication.drawio#%7B%22pageId%22%3A%22Oxd-Gnnp0cI7EY-jCEC0%22%7Dc)
- **August 19** - Telemetry link established video
- **Sept 2** - System redesign with only 1 MCU (show spinning around in Blender)
- **Sept 9** - [new single-MCU firmware re-write and validation](https://i.imgur.com/yAb3jwA.jpeg)
- **Sept 16** - [electronics fully assembled](https://i.imgur.com/SLMsiLm.jpeg)
- **Sept 16** - [on its own power test](https://i.imgur.com/6nJj4Lw.jpeg)
- **Sept 22** - [motors mounted](https://i.imgur.com/xIzRuNG.jpeg) and [ESCs mounted](https://i.imgur.com/4QXQ7te.jpeg)
- **Sept 23** - first motor spin test (20250923_142723.mp4)
- **Oct 8** - organizing wires w/ zip tie, [before](https://i.imgur.com/3tY9PoY.jpeg) and [after](https://i.imgur.com/HdgoDug.jpeg)
- **Oct 23** - propellers mounted, battery strapped down. Ready for PID tuning! [pic](https://i.imgur.com/EKcOXxi.jpeg)
- **Oct 24** - [first spin test w/ motors, held down](https://x.com/TimHanewich/status/1981800056358604926/video/1)
- **Oct 25** - Trying to find PID ratios (see vid of me holding it in hand from desk view)
- **Oct 25?** - [severe oscilations in test](https://x.com/TimHanewich/status/1982564239979270625/video/1), see vid of setting it up on bed too
- **Oct 26** - [first flight!](https://x.com/TimHanewich/status/1982566777273163850/video/1)
- **Nov 1** - [added onboard telemetry logging](https://www.youtube.com/watch?v=hwmNH4gt-zs)
- **Nov 2** - first outdoor flight. Show taking off perspective from ground, then reverse onboard high up. Then it landing from 3rd perspective.