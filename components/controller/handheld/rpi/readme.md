# Pi Code
Just a lightweight script for reading controller input and then providing that to the Pi Pico via UART.

## Set Up
Below I have listed the steps to get a Raspberry Pi prepared to serve as the broker between the microcontroller (i.e. Raspberry Pi Pico) and any USB controller plugged into the Pi (i.e. Xbox controller):

1. Flash Raspbian Server to a micro SD card
2. Use `git` to clone this repo.
3. Create a virtual environment with `python -m venv myvenv` (makes a virtual environment called *myvenv*) and activate it with `source myvenv/binactive`
4. Install the required packages from [requirements.txt](./src/requirements.txt): `pip install -r requirements.txt`
5. Enable serial comms: `sudo raspi-config` --> Interface Options --> Serial Port --> "No" to login shell accessible over serial --> "Yes" to serial port hardware enabled.
6. Run [main.py](./src/main.py) to validate it works as expected
7. Set it up to run right on boot up
    1. `crontab -e` to edit crontab
    2. Add a `@reboot` line: `@reboot /home/pi/myproject/venv/bin/python /home/pi/myproject/main.py`. NOTE: in this line, it is running the exact python executable in the venv - *that* is how to run it via a venv (no need to activate it necessarily). **So you will have to find the exact path to the python executable and in your venv and the exact path to main.py**
8. Upon rebooting, if you want to see it working, run something like `ps aux | grep main.py`