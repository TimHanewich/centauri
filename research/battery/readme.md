# Battery Reading
I want to get as accurate as a battery reading as possible. I was originally "backing in" to the battery voltage by using proportions from the ADC pin's 3.3v max, but that slightly underestimates the battery's voltage by something like 0.5-0.8 volts (around there I think).

Instead, I wrote [this test](./test_src/) that runs on the drone. I then supply varying levels of voltages (see below) and observe what ADC value it is reporting back. I can then do some linear math to determine the correct voltage reading at any ADC reading!

## Results
|Supply Voltage|ADC Reading (uint16)|
|-|-|
|16.8|57,331|
|14.1|48,306|
|11.4|39,256|
|8.7|30,008|
|6.0|21,058|

Using Excel's `=LINEST()` on those above results (using ADC reading as X's and Supply Voltage as Y), we arrive at the following `m` and `b` values in the equation `y = mx + b`:
- `m` = 0.000297206685231603
- `b` = -0.248064966259934