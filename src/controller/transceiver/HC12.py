"""
HC12.py MicroPython driver for the HC-12 wireless serial communication module
Author Tim Hanewich, github.com/TimHanewich
Find updates to this code: https://github.com/TimHanewich/MicroPython-Collection/tree/master/HC-12

MIT License
Copyright 2025 Tim Hanewich
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import machine
import time

class HC12:

    def __init__(self, uart:machine.UART, SET_pin:int):

        # primary I/O (UART and the SET pin)
        self._uart = uart
        self._set_pin = machine.Pin(SET_pin, machine.Pin.OUT)

        # Internal process variables
        self._rx_buffer:bytearray = bytearray()
        self._procTime:float = 0.15 # standard processing time used across functions

        # set up
        self._uart.init(baudrate=9600, timeout=200, timeout_char=10) # re-init with required param values
        self._uart.read() # clear RX buffer

    def _flush_rx(self) -> int:
        """Read all bytes on the UART RX buffer and bring them into an internal buffer. Returns the number of new bytes that were read and captured."""
        bytes_available:int = self._uart.any()
        if bytes_available > 0: # if there is data to receive
            new_data:bytes = self._uart.read(bytes_available)
            self._rx_buffer = self._rx_buffer + new_data
            return len(new_data)
        else:
            return 0

    def receive(self) -> bytes:
        """Returns any bytes that have been received (intentionally excludes any AT command responses)."""
        self._flush_rx() # read anything else awaiting on the UART RX buffer
        ToReturn:bytes = bytes(self._rx_buffer) # prepare to return
        self._rx_buffer = bytearray() # clear the internal RX buffer
        return ToReturn
    
    def send(self, data:bytes) -> None:
        """Sends data via the HC-12."""
        self._set_pin.high() # put set pin in high, its normal state for sending data (not sending AT commands)... it should be in this anyway, but doing it again to be sure.
        self._uart.write(data)
    
    @property
    def pulse(self) -> bool:
        try:
            response = self._command_response("AT\r\n".encode())
            return response == "OK\r\n".encode()
        except:
            return False
            
    @property
    def channel(self) -> int:
        """Checks which channel the HC-12 is currently operating on."""
        response:bytes = self._command_response("AT+RC\r\n".encode())
        responseSTR:str = response.decode()
        if responseSTR.startswith("OK+RC"):
            return int(responseSTR[5:])
        else:
            raise Exception("Unable to extract channel value from HC-12 response '" + str(response) + "'.")
        
    @channel.setter
    def channel(self, ch:int) -> None:

        if ch < 1 or ch > 127:
            raise Exception("Unable to set channel to '" + str(ch) + "'. Must be between 1 and 127.")

        # Get channel as 00# (3 digits)
        chstr:str = str(ch)
        while len(chstr) < 3:
            chstr = "0" + chstr

        # set the channel
        setter:str = "AT+C" + chstr + "\r\n"
        response:bytes = self._command_response(setter.encode())
        if "OK+C".encode() not in response:
            raise Exception("Setting to channel '" + str(ch) + "' failed!")

        
    @property
    def power(self) -> int:
        """
        Checks the transmitter power the HC-12 is currently using, from 1-8.
        Level 1 = -1 dBm
        Level 2 = 2 dBM
        Level 3 = 5 dBM
        Level 4 = 8 dBM
        Level 5 = 11 dBM
        Level 6 = 14 dBM
        Level 7 = 17 dBM
        Level 8 = 20 dBM
        """
        response:bytes = self._command_response("AT+RP\r\n".encode())
        responseSTR:str = response.decode()  # 'b'OK+RP:-01dBm\r\n'', 'b'OK+RP:+20dBm\r\n''
        if responseSTR.startswith("OK+RP:"):
            dBm:int = int(responseSTR[7:9])
            if dBm == -1:
                return 1
            elif dBm == 2:
                return 2
            elif dBm == 5:
                return 3
            elif dBm == 8:
                return 4
            elif dBm == 11:
                return 5
            elif dBm == 14:
                return 6
            elif dBm == 17:
                return 7
            elif dBm == 20:
                return 8
        else:
            raise Exception("Unable to extract transmitting power value from HC-12 response '" + str(response) + "'.")
        
    @power.setter
    def power(self, level:int) -> None:
        """Set the transmitting power to a level between 1-8."""
        asstr:str = "AT+P" + str(level) + "\r\n"
        response:bytes = self._command_response(asstr.encode())
        if "OK+P".encode() not in response:
            raise Exception("Unable to set transmitting power to " + str(level) + "!")
        
    @property
    def mode(self) -> int:
        """
        Returns the transmission mode of the HC-12 ("FU", i.e. FU1, FU2, etc.), either 1, 2, 3, or 4
        
        FU1: Moderate power usage with fast air transmission and wide UART baud range.
        FU2: Ultra low-power mode ideal for battery life, but with slow UART limits.
        FU3: Default mode offering solid reliability with moderate speed and current draw.
        FU4: Long-range mode with the lowest air speed, best for sparse, distant data.

        Detailed mode description: https://i.imgur.com/6x1I2YQ.png
        """

        # We have to handle this one differently than using the ._command_response() function because this one gives a whole bunch of lines and takes a moment.
        # there is no way to get ONLY the transmission mode (FU) with a commmand. We have to ask for all the parameters and parse it out

        # enter into AT mode
        self._set_pin.low() # pull it low to go into AT mode
        time.sleep(self._procTime) # wait a moment for AT mode to be realized

        # flush the existing buffer so what we get next is for sure the response from the AT command
        self._flush_rx()

        # write AT command
        self._uart.write("AT+RX\r\n".encode())

        # get full response
        # the last part of the transmission should be the OK+FU, what we are looking for
        started_at_ticks_ms:int = time.ticks_ms()
        response:bytes = bytes()
        while "OK+FU".encode() not in response or (time.ticks_ms() - started_at_ticks_ms) > 1000:
            time.sleep(self._procTime)
            data:bytes = self._uart.readline()
            if data != None:
                response = response + data

        # enter back into normal mode
        self._set_pin.high()

        # parse out transmission mode (FU)
        if response.endswith("OK+FU1\r\n".encode()):
            return 1
        elif response.endswith("OK+FU2\r\n".encode()):
            return 2
        elif response.endswith("OK+FU3\r\n".encode()):
            return 3
        elif response.endswith("OK+FU4\r\n".encode()):
            return 4
        else:
            raise Exception("Unable to interpret transmission mode from response '" + str(response) + "'")
    
    @mode.setter
    def mode(self, mode:int) -> None:
        """Set the transmission mode of the HC-12 as FU1, FU2, FU3, or FU4."""
        if mode not in [1,2,3,4]:
            raise Exception("Transmission mode must be either 1, 2, 3, or 4.")
        cmd:str = "AT+FU" + str(mode) + "\r\n"
        response:bytes = self._command_response(cmd.encode())
        if "OK+FU".encode() not in response:
            raise Exception("Setting transmission mode to " + str(mode) + " was not successful. Response from HC-12 was '" + str(response) + "'")

    def sleep(self) -> None:
        """Puts the HC-12 in sleep mode where receiving is suspended with very low power consumption."""
        response:bytes = self._command_response("AT+SLEEP\r\n".encode())
        if response != "OK+SLEEP\r\n".encode():
            raise Exception("Failed to put HC-12 into sleep mode.")

    @property
    def firmware(self) -> str:
        """Return firmware version information on HC-12 module."""
        response:bytes = self._command_response("AT+V\r\n".encode())
        if response == None:
            return response
        else:
            return response.decode()
        
    def reset(self) -> None:
        """Reset HC-12 to default baud rate, channel, and transmission mode."""
        response:bytes = self._command_response("AT+DEFAULT\r\n".encode())
        if response != "OK+DEFAULT\r\n".encode():
            raise Exception("Failed to reset HC-12 back to defaults.")
        
    @property
    def status(self) -> dict:
        """Returns a summary of all settings."""
        try:
            ToReturn = {}
            ToReturn["channel"] = self.channel
            ToReturn["power"] = self.power
            ToReturn["mode"] = self.mode
            return ToReturn
        except Exception as ex:
            raise Exception("Unable to acquire status values! Internal error: " + str(ex))

    def _command_response(self, cmd:bytes) -> bytes:
        """Brokers the sending of AT commands and collecting a response. Returns None if nothing was received."""

        # enter into AT mode
        self._set_pin.low() # pull it low to go into AT mode
        time.sleep(self._procTime) # wait a moment for AT mode to be realized

        # flush the existing buffer so what we get next is for sure the response from the AT command
        self._flush_rx()

        # write AT
        self._uart.write(cmd)

        # wait for response
        response:bytes = self._uart.readline()

        # enter back into normal mode
        self._set_pin.high()

        return response