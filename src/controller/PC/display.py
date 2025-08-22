import os
import shutil
import rich.table
import time

# define console-clearing command
def cls() -> None:
    if os.name == "nt": # windows NT, like windows 10 or windows 11, the modern windows
        os.system("cls")
    else: # if on linux, just run clear
        os.system("clear")

# define message structure
class Message:
    def __init__(self, time_seconds:float, msg:str):
        self.time:float = time_seconds
        self.message = msg

# define display function
class DisplayPack:
    def __init__(self):

        # system info
        self.packets_sent:int = 0
        self.packets_received:int = 0
        self.packet_last_received_ago_ms:int = 0

        # controls being sent to drone
        self.armed:bool = False
        self.mode:bool = False # False = Rate, True = angle
        self.throttle:float = 0.0 # 0.0 to 1.0
        self.pitch:float = 0.0
        self.roll:float = 0.0
        self.yaw:float = 0.0

        # telemetry being received from the drone: system status:
        self.drone_battery:float = 0.0 # battery voltage
        self.tf_luna_distance:int = 0 # distance, in CM
        self.tf_luna_strength:int = 0
        self.altitude:float = 0.0 # altitude as detected by BMP180
        self.heading:int = 0 # heading as detected by QMC5883L

        # telemetry being received from drone: control status
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
        self.messages:list[Message] = []

def construct(dp:DisplayPack) -> rich.table.Table:
    """Construct the telemetry table to dispaly"""

    # check size of console
    size = shutil.get_terminal_size()
    TerminalWidth = size.columns # how wide the console is, in characters

    # determine width of all three columns
    width_system:int = int(TerminalWidth * 0.2) # 20% of console
    width_controls:int = int(TerminalWidth * 0.2) # 20% of console
    width_telemetry:int = int(TerminalWidth * 0.2) # 20% of console
    width_messages:int = TerminalWidth - width_controls - width_telemetry

    # construct table
    table:rich.table.Table = rich.table.Table()
    table.title = "Centauri Control"
    table.add_column("System Info", width=width_system)
    table.add_column("Control Input", width=width_controls)
    table.add_column("Drone Status", width=width_telemetry)
    table.add_column("Drone Messages", width=width_messages)

    # construct what to display for system info
    txt_system:str = ""
    txt_system = txt_system + "Packets Sent: " + str(dp.packets_sent)
    txt_system = txt_system + "\n" + "Packets Recv: " + str(dp.packets_received)
    if dp.packet_last_received_ago_ms != None:
        last_recv_seconds:int = int(dp.packet_last_received_ago_ms / 1000) # int() rounds down, which I want here
        txt_system = txt_system + "\n" + "Last Recv: " + str(last_recv_seconds) + " s"
    else:
        txt_system = txt_system + "\n" + "Last Recv: [red]never[/]"
    txt_system = "[grey70]" + txt_system + "[/]" # wrap the whole thing in a grey color

    # construct what to display in controls column
    txt_controls:str = ""
    if dp.armed:
        txt_controls = txt_controls + "[bold][blue]ARMED[/][/]"
    else:
        txt_controls = txt_controls + "Unarmed"
    if dp.mode == False:
        txt_controls = txt_controls + "\n" + "[bold]Rate[/] mode"
    else:
        txt_controls = txt_controls + "\n" + "[bold]Angle[/] mode"
    input_style:str = "blue bold" if dp.armed else "grey89"
    txt_controls = txt_controls + "\n" + "Throttle: [" + input_style + "]" + str(int(dp.throttle * 100)) + "%[/]"
    txt_controls = txt_controls + "\n" + "Pitch: [" + input_style + "]" + str(int(dp.pitch * 100)) + "%[/]"
    txt_controls = txt_controls + "\n" + "Roll: [" + input_style + "]" + str(int(dp.roll * 100)) + "%[/]"
    txt_controls = txt_controls + "\n" + "Yaw: [" + input_style + "]" + str(int(dp.yaw * 100)) + " %[/]"

    # construct what to display in telemety column (telemetry from quadcopter)
    txt_status:str = ""
    txt_status = txt_status + "Battery: " + str(round(dp.drone_battery, 1)) + " v"
    txt_status = txt_status + "\n" + "LunaD: " + str(dp.tf_luna_distance) + " cm"
    txt_status = txt_status + "\n" + "LunaS: " + str(dp.tf_luna_strength)
    txt_status = txt_status + "\n" + "Altitude: " + str(round(dp.altitude, 1)) + " m"
    txt_status = txt_status + "\n" + "Heading: " + str(dp.heading) + " °"
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
    messages_to_display:list[Message] = [] # create empty list
    messages_to_display.extend(dp.messages) # copy all
    while len(messages_to_display) > max_messages: # until it fits...
        messages_to_display.pop(0) # remove the first
    txt_messages:str = ""
    for msg in messages_to_display:

        # figure out delay
        SecondsAgo:int = int(time.time() - msg.time)

        # determine message
        ThisMsg:str = SecondsAgo + "s ago: " + msg.message

        # trim if needed
        if ThisMsg > width_messages:
            ThisMsg[0:width_messages-3] + "..."

        # append it
        txt_messages = txt_messages + ThisMsg + "\n"
        
    if len(txt_messages) > 0:
        txt_messages = txt_messages[0:len(txt_messages)-1] # trim off last newline


    table.add_row(txt_system, txt_controls, txt_status, txt_messages)
    return table