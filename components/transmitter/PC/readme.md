# Transmitter Program
The transmitter software, [main.py](./src/PC/main.py), serves as the communication hub between the pilot and the quadcopter. It continuously processes inputs from the Xbox controller, encodes them into compact data packets, and relays them to the drone via the transceiver.

At its core, the program runs an infinite loop with three main steps:
1. **Read inputs** from the Xbox controller  
2. **Encode inputs** into a dense, structured data packet  
3. **Transmit packets** to the USB‑connected transceiver, which forwards them wirelessly to the quadcopter  

Beyond sending commands, the program also **receives telemetry** broadcasted back from the drone, such as battery status, flight rates, and error messages, and can **update PID settings on the fly**, allowing real‑time tuning of flight performance.

Key libraries used:
- **[pygame](https://pypi.org/project/pygame/)** - captures Xbox controller input  
- **[rich](https://pypi.org/project/rich/)** - renders a live telemetry dashboard during operation  
- **[pyserial](https://pypi.org/project/pyserial/)** - manages serial communication with the transceiver  
- **[keyboard](https://pypi.org/project/keyboard/)** - detects pilot keyboard commands for adjusting settings  

## Getting up and running
Note that **python version 3.12** must be installed and used as I have learned the **pygame** module is best on it.

If you need to install python version 3.12:

```
py install 3.12
```

### Step 1: Create and Activate a Virtual Environment
First navigate into the `src` folder in a terminal.

Create a virtual environment specifically using version 3.12:

```
py -3.12 -m venv centauri_venv
```

### Step 2: Activate the virtual environment!
On windows:

```
centauri_venv\Scripts\activate.bat
```

On Linux:

```
source centauri_venv/bin/activate
```

### Step 3: Install requirements
Run:

```
python -m pip install -r requirements.txt
```

### Step 4: Run!
Now you can run the program! Run:

```
python main.py
```