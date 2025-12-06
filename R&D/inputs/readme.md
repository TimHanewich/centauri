# Testing Python's "inputs" module

Module here: https://pypi.org/project/inputs/

## Example Tests Here
- Basic reading Xbox controller inputs test: [test_read.py](./test_read.py)
- Having a separate thread for reading the inputs: [test_nonblocking.py](./test_nonblocking.py) *(you will need to do this because reading the controller input is blocking)*
- Testing if controller connected/disconnected and continue working in event of disconnect/reconnect: [test_connected.py](./test_connected.py) (**THIS IS HOW WE WILL READ** - `get_gamepad()` doesn't working with the `DeviceManager()` connectivity check)