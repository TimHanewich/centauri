import os
import shutil
import rich.table
import rich.console
import time
import random

# define console-clearing command
def cls() -> None:
    if os.name == "nt": # windows NT, like windows 10 or windows 11, the modern windows
        os.system("cls")
    else: # if on linux, just run clear
        os.system("clear")



# define display function
class DisplayPack:
    def __init__(self):

        # controls being sent to drone
        self.armed:bool = False
        self.mode:bool = False # False = Rate, True = angle
        self.throttle:float = 0.0 # 0.0 to 1.0
        self.pitch:float = 0.0
        self.roll:float = 0.0
        self.yaw:float = 0.0

        # telemetry being received from drone
        self.drone_battery:float = 0.0 # battery voltage or battery level?
        self.M1_throttle:float = 0.0 # 0.0 to 1.0
        self.M2_throttle:float = 0.0
        self.M3_throttle:float = 0.0
        self.M4_throttle:float = 0.0
        self.pitch_rate:float = 0.0
        self.roll_rate:float = 0.0
        self.yaw_rate:float = 0.0
        self.pitch_angle:int = 0 # -90 to 90
        self.roll_angle:int = 0 # -90 to 90

def display(dp:DisplayPack) -> None:

    # clear console
    cls()

    # check size of console
    size = shutil.get_terminal_size()
    TerminalWidth = size.columns # how wide the console is, in characters

    table:rich.table.Table = rich.table.Table()
    table.title = "Centauri Control"
    table.add_column("Controls")
    table.add_column("Status")
    table.add_column("Messages")

    
