# MBED Code 

This is the new code for the MBEDs that replaced the Arduinos in the rover. Detailed here is also the communication protocol from Mission Control to the MBEDs.

Packet structure:
\<start><0x00><1><2><3><4><5><6>\<cs>

\<start> = 0xab

Each wheel speed will be a signed byte where -126 is reverse and 126 is forward.