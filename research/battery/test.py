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