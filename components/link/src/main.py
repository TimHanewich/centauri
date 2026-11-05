##### SETTINGS #####

# SSD1306 I2C
ssd1306_bus:int = 1
ssd1306_sda:int = 2
ssd1306_scl:int = 3

# HC12 UART
hc12_bus:int = 1
hc12_txd:int = 4
hc12_rxd:int = 5
hc12_set:int = 6

# Push Button
button_gpio:int = 7

# Battery ADC (voltage divider)
vbat_adc_gpio:int = 26

# Battery-detecting setting: alpha
# Higher values closer to 1.0 = slower average
# Lower values closer to 0.0 = fast response
vbat_alpha:float = 0.99

# Control Packet to broadcast in send mode
command_packet:bytes = b'\x00\x00\x00\x80\x00\x80\x00\x80\x00\x81\x06'   # 0% throttle, 0% pitch, 0% roll, 0% yaw.    Constructed on November 5, 2026.

####################


import machine
import ssd1306
import display
from HC12 import HC12
from tools import unpack_control_packet
from BatteryMonitor import BatteryMonitor, PROFILE_18650

# load on screen
print("Setting up I2C...")
i2c = machine.I2C(ssd1306_bus, sda=machine.Pin(ssd1306_sda), scl=machine.Pin(ssd1306_scl))
print("Polling I2C devices...")
i2c_devices:list[int] = i2c.scan()
print("I2C devices: " + str(i2c_devices))

# if no SSD-1306
if 60 not in i2c_devices:
    print("Error! SSD-1306 not connected. Stopping.")
    exit()
else:
    print("SSD-1306 connected!")

# set up OLED
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
d:display.Display = display.Display(oled)

# Show CENTAURI logo for a moment
d.show(display.SCREEN_CENTAURI)
import time
time.sleep(2.0)

# Set up HC12
d.status("Setting up HC-12")
uart = machine.UART(hc12_bus, rx=machine.Pin(hc12_rxd), tx=machine.Pin(hc12_txd), baudrate=9600)
hc12 = HC12(uart, hc12_set)

# Pulse HC12
d.status("Pulsing HC-12...")
pulsed:bool = False
pulse_attempt:int = 1
while pulsed == False:
    d.status("Pulse #" + str(pulse_attempt))
    pulsed = hc12.pulse
    if not pulsed:
        d.status("Pulse #" + str(pulse_attempt) + " fail")
        time.sleep(1.0)
        pulse_attempt = pulse_attempt + 1

# confirm HC-12 pulse successful
d.status("HC-12 pulsed!")
time.sleep(0.2)

# Configure HC-12: mode FU3
d.status("Set HC-12 mode...")
hc12.mode = 3
time.sleep(0.2)
d.status("Confirming...")
if hc12.mode == 3:
    d.status("FU3 good!")
else:
    d.status("HC12 mode fail!")
    exit()
time.sleep(0.5)

# Configure HC-12: channel
d.status("Set HC-12 Channel")
hc12.channel = 2
time.sleep(0.2)
d.status("Confirming...")
if hc12.channel == 2:
    d.status("Channel good!")
else:
    d.status("Channel fail")
    exit()
time.sleep(0.5)

# Configure HC-12: power
d.status("Set HC-12 Power")
hc12.power = 8
time.sleep(0.2)
d.status("Confirming...")
if hc12.power == 8:
    d.status("Power good!")
else:
    d.status("Power fail")
    exit()
time.sleep(0.5)

# set up battery ADC
battery_adc = machine.ADC(machine.Pin(vbat_adc_gpio))
battery_monitor:BatteryMonitor = BatteryMonitor(PROFILE_18650)
battery_voltage_carried:float = None # start with null value

# set up button
BUTTON = machine.Pin(button_gpio, machine.Pin.IN, machine.Pin.PULL_UP)
def button_pressed() -> bool:
    if BUTTON.value() == 1:
        return False
    else:
        return True

# Set up static enums
MODE_RECV:int = 0
MODE_SEND:int = 1

# Set up vars: general
mode:int = MODE_RECV            # start in RECV mode (default)

# Set up vars: RECV mode
rxbuffer:bytearray = bytearray()
control_input:list[int] = [0, 0, 0, 0]             # used to "unpack" control data into (dummy, not used in this project but necessary for the unpack code lifted out of the flight controller)
recv_count:int = 0
last_recv_at_ticks_ms:int = time.ticks_ms()        # just start at right now

# Set up vars: SEND mode
packets_sent_count:int = 0
packet_last_sent_ticks_ms:int = time.ticks_ms()                             # just mark right now
command_packet_to_send:bytes = command_packet + "\r\n".encode()             # append the "\r\n" terminator to it so we don't have to do it each and every time later in a loop. THIS will be what we send.

# press button to start
d.show(display.SCREEN_PRESS_BUTTON) # show press button
while True:

    # wait a moment
    time.sleep(0.01)

    # check if pressed
    if button_pressed():
        break # get out of while loop

# go to normal display mode!
while True:

    # get battery voltage (from ADC)
    vbat_reading:int = battery_adc.read_u16()
    battery_voltage:float = 3.01 + (((vbat_reading - 38800) / (54000 - 38800)) * (4.21 - 3.01))                         # calculate the voltage on the pin based upon a test of known values (tested reading at 4.2V and reading at 3.0V)
    if battery_voltage_carried == None:                                                                                 # if we do NOT have a carried value
        battery_voltage_carried = battery_voltage                                                                       # then just start with this reading!
    else:                                                                                                               # If we DO have a carried value
        battery_voltage_carried = (battery_voltage_carried * vbat_alpha) + (battery_voltage * (1 - vbat_alpha))         # then calculated the moving average
    soc_approx:float = battery_monitor.soc(battery_voltage_carried)                                                     # get state of charge (percent) as an estimate using a lookup table
    d.battery_soc = soc_approx                                                                                           # add in SOC estimate as a percent directly (0.0 to 1.0)

    if mode == MODE_RECV:

        # check if any bytes available
        #print("Checking RX bytes available...")
        recv:bytes = hc12.receive()
        if recv != None:
            if len(recv) > 0:
                #print("Received bytes of length " + str(len(recv)))
                rxbuffer.extend(recv)

        # packet available?
        if "\r\n".encode() in rxbuffer:
            term_loc:int = rxbuffer.find("\r\n".encode(), 0)

            # "bite off" that line
            line:bytearray = rxbuffer[0:term_loc]               # the line, excluding the \r\n
            rxbuffer = rxbuffer[term_loc + 2:]                  # set the rxbuffer to everything after the line and the \r\n

            # is line a Centauri Control Packet from the Transmitter?
            # Example packets from October 22, 2026
            # Control Packet from Transmitter:
            # b'\x00@\x00\xbf\xff@\x00\x8f\xff\xcf\xa0\r\n'              (13 bytes with the \r\n, 11 bytes excluding it)
            # Status Packet from Quadcopter:
            # b'\x00}\x8a^\x83T\xb7\r\n'                                 (9 bytes with the \r\n, 7 bytes excluding it)
            if len(line) == 11: # so only attempt if the length is 11, which would be a Control Packet from the transmitter
                unpacked:bool = unpack_control_packet(line, control_input)
                if unpacked:
                    recv_count = recv_count + 1
                    last_recv_at_ticks_ms = time.ticks_ms()

            # plug in: count received
            d.packets_received_count = recv_count
        
            # plug in: last recv ago (ms span)
            ticks_ms_since_last_recv:int = time.ticks_diff(time.ticks_ms(), last_recv_at_ticks_ms)
            d.since_last_recv_ticks_ms = ticks_ms_since_last_recv

            # Refresh display in RECV mode
            d.show(display.SCREEN_RECV)

        elif mode == MODE_SEND:

            # calculate time since a packet was LAST sent out
            time_since_last_packet_sent_ticks_ms:int = time.ticks_diff(time.ticks_ms(), packet_last_sent_ticks_ms)

            # if we have not sent one in time, send one
            transmission_rate_hz:int = 20                                           # how many time the transmitter broadcasts a command packet per second
            ms_between_transmissions:int = 1000 / transmission_rate_hz              # how many ms should be between each transmission
            if time_since_last_packet_sent_ticks_ms >= ms_between_transmissions:

                # broadcast
                hc12.send(command_packet_to_send)

                # update last sent time
                packet_last_sent_ticks_ms = time.ticks_ms()

                # increment sent count
                packets_sent_count = packets_sent_count + 1

            # Refresh display in SEND mode
            d.show(display.SCREEN_SEND)    
    
    # slight wait
    time.sleep(0.01) # 100 Hz refresh rate