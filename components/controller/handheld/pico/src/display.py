import ssd1306
import framebuf

class Display:

    def __init__(self, oled:ssd1306.SSD1306_I2C):
        self._oled = oled

        # unique identifier for the "page" we are on right now
        # Could be: 
        # "awaiting_ci" = awaiting controller input
        # "awaiting_start" = press start button to begin (just after CI received)
        # "home" = main home screen
        # "pid confirm" = confirm they want to send over pre-flashed PID settings
        # "send pid" = currently sending pid (or waiting for confirmation)
        # "logo" = Centauri logo
        # "ci_problem" = control input problem
        # "boot" = screen while loading
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

        # "boot" screen
        self.boot_status:str

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
            self._oled.text("Input", 44, 20)
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
        elif self.page == "logo":
            CENTAURI_GRAPHIC = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xfc\x00\x7f\xc0?\x07\xf8\xe0\xcf\xfc8\x188\xff\x0c\x01\xf0\x00\x1e\x00\x7f\x87\xf8\xe0\xcf\xfcx\x188\xff\x8c\x00\xf0\x00\x1e\x00\xe1\xc6\x00\xf0\xc1\xc0|\x188\xc3\x8c\x00\xd8\x00$\x00\xc0\xc6\x00\xf8\xc1\xc0|\x188\xc1\x8c\x00\x0c\x00d\x01\xc0\x06\x00\xf8\xc1\xc0\xec\x188\xc3\x8c\x00\x06\x00\xc0\x01\xc0\x07\xf8\xdc\xc1\xc0\xce\x188\xff\x8c\x00\x03\x01\x80\x01\xc0\x07\xf8\xcc\xc1\xc1\xc6\x188\xff\x0c\x00\x01\xc7\x00\x01\xc0\x07\x00\xce\xc1\xc1\xc7\x188\xfe\x0c\x00\x00\xfe\x00\x01\xc0\x86\x00\xc7\xc1\xc1\xff\x188\xc7\x0c\x00\x00\xfe\x00\x00\xe0\xc6\x00\xc7\xc1\xc3\xff\x1c8\xc3\x0c\x00\x00\xfe\x00\x00\xf3\xc7\x00\xc3\xc1\xc3\x83\x9cx\xc3\x8c\x00\x00\xfe\x00\x00\x7f\x87\xfc\xc1\xc1\xc7\x03\x8f\xf0\xc1\xcc\x00\x00\xfe\x00\x00?\x07\xf8\xc1\xc0\xc7\x01\x87\xe0\xc1\xcc\x00\x00\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x80\x00p\x03\x00\xf0q\xc8=\xc3\x00\x070\x00\x0c\x00D\x00B$\x82 \x9al\x91$\x90\x88L\x00\xd8\x00$\x00B(\x12 \x84,\x91(P\x88D\x00\xf0\x00\x1e\x00r)\x9e \x04*\x91\xc8P\x8fx\x00\xf0\x00\x1e\x00B(\x02 \x82)\x91(P\x88H\x07\xfc\x00\x7f\xc0B$\x82 \xd3I\x91$\x90\x8cD\x00\xc0\x00\x0e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            graphic = framebuf.FrameBuffer(CENTAURI_GRAPHIC, 128, 64, framebuf.MONO_HLSB)
            self._oled.blit(graphic, 0, 0)
            self._oled.show()
        elif self.page == "ci_problem":
            self._oled.text("Controller", 24, 10)
            self._oled.text("Input", 44, 20)
            self._oled.text("Problem!", 32, 30)
        elif self.page == "boot":
            self._oled.text("Booting...", 32, 20)
            txt:str = self.boot_status
            xpos:int = int((128 - (len(txt) * 8)) / 2)
            self._oled.text(txt, xpos, 34)
        elif self.page == "awaiting_start":
            self._oled.text("Ready!", 40, 22)
            self._oled.text("Press START", 20, 34)
        else:
            self._oled.text("UNKNOWN PAGE", 0, 0)

        # show
        self._oled.show()

# import machine
# i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
# oled = ssd1306.SSD1306_I2C(128, 64, i2c)
# d = Display(oled)
# d.page = "ci_problem"
# d.display()