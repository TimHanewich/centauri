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

## Estimating Battery Voltage from an ADC Reading
The code below, as shown in [test_calculation.py](./test_calculation.py), shows how we can estimate the supply voltage from only an ADC reading:

```
adc_vals:list[int] = [57331, 48306, 39256, 30008, 21058]

# declare M and B from y = mx + b
# These are from the =LINEST function in Excel
# however, I multiplied both by 1,000,000 to get them as integers, not floating point numbers (so we can do integer math which is quicker)
m:int = 297
b:int = -248065

# demonstrate inferring voltage from each
for adc_val in adc_vals:
    
    # we can back into a floating point number like so:
    # the original formula was:     voltage:int = (b + (adc_val * m)) // divisor
    # however, because of integer division, it will always truncate "the remainder" and thus not round up
    # a classic fix for this, thanks to GPT-5 telling me, is to add half of the divisor to the numerator before dividing. This aparently makes it round up
    # also: note that we are not dividing by the ORIGINAL scaler of 1,000,000 (that we scaled the m and b values to). That would have been what we are supposed to do if we want the result to be a floating point number (i.e. 16.8 volts)
    # we do NOT want a floating point number - we want an integer! Because integer math is much faster
    # So, I integer divide by 100,000 (10x less than 1,000,000) to get a value like 168 instead of 16.8 (10x higher and no decimals to deal with)
    # So, every voltage value we calculate should be between 60 and 168, inclusive.
    divisor:int = 100_000
    voltage:int = ((b + (adc_val * m)) + (divisor // 2)) // divisor

    print(str(adc_val) + " = " + str(voltage) + " volts")
```

## Performance Considerations
I also checked performance as that is *very* important in a quadcopter flight controller: see [test_performance.py](./test_performance.py).
- The "old way": **~135 us, 0 bytes of new memory used**
- The "new way": **~135 us, 0 bytes of new memory used**