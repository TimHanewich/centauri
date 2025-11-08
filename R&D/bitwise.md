# Bitwise Operations
In Python, we can use `<<` to perform a bitwise left shift. For example `1` is `00000001`. If we shift it to the left one time, it would be `00000010`.

|Notation|Value|
|-|-|
|`1 << 0`|`0b00000001`|
|`1 << 1`|`0b00000010`|
|`1 << 2`|`0b00000101`|
|`1 << 3`|`0b00001000`|
|`1 << 4`|`0b00010000`|
|`1 << 5`|`0b00100000`|
|`1 << 6`|`0b01000000`|
|`1 << 7`|`0b10000000`|

### OR Operator
A `OR` operation compares each bit between two bytes you give it (compares bits of the same position). Between the two bits being compared, if **at least one** of the bits are `1`, the resulting bit vaue of that position will be `1`. But if both are `0`, the resulting bit of that position will be `0`.

For example:
```
val = 1 << 0 | 1 << 1
bin(val) # 0b00000011
```

As seen above, `0b00000001` and `0b00000010` became `0b00000011` with the OR operator (`|`).

So, we can use the OR operator to set certain bit values. 

For example, if we can to construct a single byte and set the 7th, 2nd, and 1st bit value to 1:
```
val = 0b00000000 # start with 0, a blank slate (can just do val=0 too)
val = val | 0b10000000 # set the 7th bit to 1
val = val | 0b00000010 # set the 2nd bit to 1
val = val | 0b00000001 # set the 1st it to 1
bin(val) # 0b10000011
```

The example above sets each bit one-by-one. We can also set them all at once, for example:
```
val = 0b00000000 # start with 0, a blank slate
val = val | 0b10000011
bin(val) # 0b10000011
```

### AND Operator
The AND operator is important as it gives us the ability to check if a certain bit of a byte is occupied or not. By doing an AND operation between a byte value and a byte value with the bit we are testing occupied as 1 (and all other bits set to 0), if the resulting value has at least that one bit occupied, that means that bit indeed was occupied by 1. If it comes back as 0, that bit was not occupied.

For example:
```
val = 0b11010010
tester = 0b10000000 
result = val & tester # bitwise AND operator
print(result) # 128
```

In the example above, since the result was not 0, we can indeed confirm the 7th bit was occupied. 

If we try that with a bit that is NOT occupied, `result` will be 0:
```
val = 0b11010010
tester = 0b00100000 
result = val & tester # bitwise AND operator
print(result) # 0
```

So, putting that all together, a quick way to test if a bit is occupied is this for example:
```
val = 0b11010010
if val & 0b10000000 > 0:
    print("7th bit is occupied!")
else:
    print("7th bit is not occupied.")
```