adc_vals:list[int] = [57331, 48306, 39256, 30008, 21058]

# declare M and B from y = mx + b
# These are from the =LINEST function in Excel
# however, I multiplied both by 1,000,000 to get them as integers, not floating point numbers (so we can do integer math which is quicker)
m:int = 297
b:int = -248065

# demonstrate inferring voltage from each
for adc_val in adc_vals:
    
    # we can back into a floating point number like so:
    divisor:int = 100_000
    voltage:int = (b + (adc_val * m)) // divisor

    print(str(adc_val) + " = " + str(voltage) + " volts")