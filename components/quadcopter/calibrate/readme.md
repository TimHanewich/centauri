# ESC Calibration Script
Electronic Speed Controllers generally require calibration as part of their setup straight out of the box. I'm providing [main.py](), a lightweight calibration script you can place on the Raspberry Pi Pico of the quadcopter to perform the calibration, setting up the four ESCs so they are ready to use.

**IMPORTANT: if using this calibration file, do so WITHOUT PROPS ON!** It is unlikely the motors will spin at all anyway, but *just in case*, ensure the props of the motors are **REMOVED** when running this script.