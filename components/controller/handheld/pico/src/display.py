import ssd1306

class Display:

    def __init__(self, oled:ssd1306.SSD1306_I2C):
        self._oled = oled

        # unique identifier for the "page" we are on right now
        # Could be: 
        # "awaiting_ci" = awaiting controller input
        # "home" = main home screen
        # "pid confirm" = confirm they want to send over pre-flashed PID settings
        # "send pid" = currently sending pid (or waiting for confirmation)
        self.page:str = "home"

        # for "home" screen
        self.last_recv:int = 0             # number of seconds since last received telemetry from drone
        self.controller_soc:float = 0.0    # between 0.0 and 1.0, the percentage charge of the controller (only a 1S lithium battery)
        self.vbat_drone:float = 0.0        # voltage of the battery on the drone (comes in from the telemetry we will receive from it)
        self.armed:bool = False            # if we are armed or not (True/False)
        self.throttle:float = 0.0          # throttle input, from 0.0 to 1.0 (percentage)
        self.pitch:float = 0.0             # pitch input, from -1.0 to 1.0
        self.roll:float = 0.0              # roll input, from -1.0 to 1.0
        self.yaw:float = 0.0               # yaw input, from -1.0 to 1.0

        # "send pid" settings
        self.send_pid_attempt:int = 0
        self.send_pid_status:str = "sending"

        # "awaiting_ci" screen
        self.seconds_waiting:int = 0

    def display(self) -> None:

        # preliminary
        self._oled.fill(0)

        if self.page == "home":

            # show the controller battery level
            controller_soc_to_display:str = str(int(round(min(max(self.controller_soc, 0.0), 0.99) * 100, 0))) + "%"
            while len(controller_soc_to_display) < 3: # ensure it is 3 characters long
                controller_soc_to_display = " " + controller_soc_to_display
            self._oled.text("C " + controller_soc_to_display, 0, 0)

            # "DRONE"
            self._oled.text("DRONE", 0, 36)
            
            # show the drone vbat level
            vbat_drone_to_display:str = str(round(self.vbat_drone, 1)) + "v"
            while len(vbat_drone_to_display) < 5:
                vbat_drone_to_display = " " + vbat_drone_to_display
            self._oled.text(vbat_drone_to_display, 0, 46)

            # last time we received telemetry (seconds)
            lastrecv_todisplay:str = str(min(max(self.last_recv, 0), 999))
            while len(lastrecv_todisplay) < 4:
                lastrecv_todisplay = " " + lastrecv_todisplay
            self._oled.text("L" + lastrecv_todisplay, 0, 56)

            # Draw vertical line to separate info pane!
            self._oled.line(46, 0, 46, 64, 1)

            # armed/unarmed
            if self.armed:
                self._oled.rect(66, 0, 41, 9, 1, 1)
                self._oled.text("ARMED", 67, 1, 0)
            else:
                self._oled.text("unarmed", 59, 1)

            # throttle
            throttle_to_display:str = str(min(max(int(round(self.throttle * 100, 0)), 0), 100)) + "%"
            while len(throttle_to_display) < 5:
                throttle_to_display = " " + throttle_to_display
            self._oled.text("T " + throttle_to_display, 59, 16)

            # pitch
            pitch_to_display:str = str(min(max(int(round(self.pitch * 100, 0)), -100), 100)) + "%"
            while len(pitch_to_display) < 5:
                pitch_to_display = " " + pitch_to_display
            self._oled.text("P " + pitch_to_display, 59, 26)

            # roll
            roll_to_display:str = str(min(max(int(round(self.roll * 100, 0)), -100), 100)) + "%"
            while len(roll_to_display) < 5:
                roll_to_display = " " + roll_to_display
            self._oled.text("R " + roll_to_display, 59, 36)

            # yaw
            yaw_to_display:str = str(min(max(int(round(self.yaw * 100, 0)), -100), 100)) + "%"
            while len(yaw_to_display) < 5:
                yaw_to_display = " " + yaw_to_display
            self._oled.text("Y " + yaw_to_display, 59, 46)

        elif self.page == "awaiting_ci":
            self._oled.text("Awaiting", 32, 0)
            self._oled.text("Controller", 24, 10)
            self._oled.text("Input", 22, 20)
            txt:str = "Waiting " + str(self.seconds_waiting)
            xpos:int = int((128 - (len(txt) * 8)) / 2)
            self._oled.text(txt, xpos, 40)
        elif self.page == "pid confirm":
            self._oled.text("Send PID?", 28, 0)
            self._oled.text("Y to confirm", 16, 10)
            self._oled.text("B to cancel", 20, 20)
        elif self.page == "send pid":

            self._oled.text("SEND PID SETTING", 0, 0)

            # Attempt #
            txt:str = "Attempt " + str(self.send_pid_attempt)
            xpos:int = int((128 - (len(txt) * 8)) / 2)
            self._oled.text(txt, xpos, 20)

            # Status
            txt:str = self.send_pid_status
            xpos:int = int((128 - (len(txt) * 8)) / 2)
            self._oled.text(txt, xpos, 30)

        else:
            self._oled.text("UNKNOWN PAGE", 0, 0)

        # show
        self._oled.show()

import machine
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

d = Display(oled)

# home
d.page = "home"
d.controller_soc = 1.0
d.vbat_drone = 16.4
d.last_recv = 1000
d.armed = False
d.throttle = 1.0
d.pitch = -1.0

# pid confrim
d.page = "pid confirm"

# send pid
d.page = "send pid"
d.send_pid_attempt = 3
d.send_pid_status = "CONFIRMED!"

d.display()