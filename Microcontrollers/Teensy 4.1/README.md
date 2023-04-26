# Teensy
Teensy 4.1 microcontrollers are currently installed on REMI. They have a very high clock speed and built-in CAN tranceivers.

## REMI Setup
The teensyEBOX program receives UDP messages from the manual_operate.py program in MissionControl. Depending on the message contents, the teensy will either update wheel speeds/LEDs, or send CAN messages to the arm/ science package. The arm contains two teensy 4.1 microcontrollers so two CAN messages are sent to the arm at a time. The arm could be ran with one Teensy but eventually encoders will be added which could lead to input delay.
