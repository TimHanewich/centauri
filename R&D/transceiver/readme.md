# 0x03 Going to REPL
The transceiver I set up is working well, except for an issue I noticed on August 27, 2025:

![issue](https://i.imgur.com/NVhSFrY.png)

The issue, shown above, is when the "Ctrl+C" terminator hits the pico over the USB, that is interpretted as a keyboard interupt (Ctrl+C), which, as we know when using Thonny for example, *cancels* the program it is running and backs out into the REPL.

This is a big problem - so whenever `0x03` (`3`) needs to be transmitted to the quadcopter and my PC sends it over the USB to the pico for it to be transmitted, the program stops? That won't work!

## Possible Solutions
We could *filter* out the `0x03`'s and replace them with a different substitute value? Doesn't seem like the natural solution.

I purchased [these USB to serial adapters](https://a.co/d/dgJtdEJ) that I will use to instead directly communicate with the Pico by connecting the adapter to its actual GPIO pins and a UART interface on there. I don't think the UART interface will interpret 0x03 as a Ctrl+C, I think that is only done on the USB.