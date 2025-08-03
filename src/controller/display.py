import os
import shutil
import rich.table

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
        self.drone_battery:float = 0.0 # battery voltage
        self.M1_throttle:float = 0.0 # 0.0 to 1.0
        self.M2_throttle:float = 0.0
        self.M3_throttle:float = 0.0
        self.M4_throttle:float = 0.0
        self.pitch_rate:float = 0.0
        self.roll_rate:float = 0.0
        self.yaw_rate:float = 0.0
        self.pitch_angle:int = 0 # -90 to 90
        self.roll_angle:int = 0 # -90 to 90

        # messages being received from the drone
        self.messages:list[str] = []

def display(dp:DisplayPack) -> rich.table.Table:

    # check size of console
    size = shutil.get_terminal_size()
    TerminalWidth = size.columns # how wide the console is, in characters

    # determine width of all three columns
    width_controls:int = int(TerminalWidth * 0.2) # 20% of console
    width_telemetry:int = int(TerminalWidth * 0.2) # 20% of console
    width_messages:int = TerminalWidth - width_controls - width_telemetry

    # construct table
    table:rich.table.Table = rich.table.Table()
    table.title = "Centauri Control"
    table.add_column("Controls", width=width_controls)
    table.add_column("Status", width=width_telemetry)
    table.add_column("Messages", width=width_messages)

    # construct what to display in controls column
    txt_controls:str = ""
    if dp.armed:
        txt_controls = txt_controls + "[bold]ARMED[/]"
    else:
        txt_controls = txt_controls + "Unarmed"
    if dp.mode == False:
        txt_controls = txt_controls + "\n" + "[bold]Rate[/] mode"
    else:
        txt_controls = txt_controls + "\n" + "[bold]Angle[/] mode"
    txt_controls = txt_controls + "\n" + "Throttle: " + str(int(dp.throttle * 100)) + "%"
    txt_controls = txt_controls + "\n" + "Pitch: " + str(int(dp.pitch * 100)) + "%"
    txt_controls = txt_controls + "\n" + "Roll: " + str(int(dp.roll * 100)) + "%"
    txt_controls = txt_controls + "\n" + "Yaw: " + str(int(dp.yaw * 100)) + " %"

    # construct what to display in telemety column (telemetry from quadcopter)
    txt_status:str = ""
    txt_status = txt_status + "Battery: " + str(round(dp.drone_battery, 1)) + " volts"
    txt_status = txt_status + "\n" + "Pitch Angle: " + str(dp.pitch_angle) + " °"
    txt_status = txt_status + "\n" + "Roll Angle: " + str(dp.roll_angle) + " °"
    txt_status = txt_status + "\n" + "Pitch Rate: " + str(dp.pitch_rate) + " °/s"
    txt_status = txt_status + "\n" + "Roll Rate: " + str(dp.roll_rate) + " °/s"
    txt_status = txt_status + "\n" + "Yaw Rate: " + str(dp.yaw_rate) + " °/s"
    txt_status = txt_status + "\n" + "M1: " + str(int(dp.M1_throttle * 100)) + "%"
    txt_status = txt_status + "\n" + "M2: " + str(int(dp.M2_throttle * 100)) + "%"
    txt_status = txt_status + "\n" + "M3: " + str(int(dp.M3_throttle * 100)) + "%"
    txt_status = txt_status + "\n" + "M4: " + str(int(dp.M4_throttle * 100)) + "%"

    # construct what to display in messages column
    max_messages:int = 10 # maxiumum number of messages that can be displayed
    messages_to_display:list[str] = [] # create empty list
    messages_to_display.extend(dp.messages) # copy all
    while len(messages_to_display) > max_messages: # until it fits...
        messages_to_display.pop(0) # remove the first
    txt_messages:str = ""
    for msg in messages_to_display:
        if len(msg) <= width_messages:
            txt_messages = txt_messages + msg + "\n"
        else: # the message exceeds the width of this column
            txt_messages = txt_messages + msg[0:width_messages - 10] + "..." + "\n"
    if len(txt_messages) > 0:
        txt_messages = txt_messages[0:len(txt_messages)-1] # trim off last newline


    table.add_row(txt_controls, txt_status, txt_messages)
    return table