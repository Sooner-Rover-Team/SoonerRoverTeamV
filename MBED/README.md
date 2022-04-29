# MBED Code

This is the new code for the MBEDs that replaced the Arduinos in the rover. Detailed here is also the communication protocol from Mission Control to the MBEDs.

Packet structure:
\<start><0x00><1><2><3><4><5><6>\<cs>

\<start> = 0xab

Each wheel speed will be an unsigned byte where 0 is reverse and 126 is stop and 252 is forward.

The wheels on the left side of the rover are numbered 0, 1, 2 starting from the front left wheel and moving backwards. Similarly, the right wheels are numbered 3, 4, 5 starting from the front right wheel and moving backwards.
