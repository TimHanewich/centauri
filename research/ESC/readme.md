# ESC Research
The [pico_pot](./pico_pot/) folder contains code that allows a Raspberry Pi Pico to act as a transmitter to an ESC using a B10K to adjust speed setting. It reads the B10K pot value and then "translates" the ananlog signal into a digital signal for the ESC. It is from my old Scout project but I also modified it here to show the output throttle % on a small SSD-1306 OLED display.

## Min Idle Throttles - Tested on August 9, 2025
Using the [pico_pot](./pico_pot/) code, I recorded the minimum throttle I had to apply to get the motors to reliably turn (not stutter in and out, turn reliably):
- Fully charged 2S (8.4v): **8%, 1,050,000 nanoseconds**
- Fully charged 3s (12.6): **6%, 1,020,000 nanoseconds**
- Fully charged 4s (16.8): **6%, 1,020,000 nanoseconds**

It seems like 6-8% is about the number, even with 10% being possible. At 10% it is a higher RPM but I don't think it would be enough to cause lift.