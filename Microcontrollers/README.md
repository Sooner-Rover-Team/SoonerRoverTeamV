# Microcontrollers
This folder contains all microcontroller code that has been used on SORO in the past. Some examples are provided for testing. The current implementation is in the Teensy 4.1 folder.

## Message Structures
### UDP
Mission Control sends UDP msgs to Ebox, which can also send CAN msgs to Arm/Science. UDP sends byteArrays, so assume each value is 0-255
- To Wheels = [0x01, 0x01, wheel0, wheel1, wheel2, wheel3, wheel4, wheel5, checkSUm]
- To LEDs = [0x01, 0x02, r, g, b, checkSum]
- To Arm = [0x02, bicep, foreArm, base, wristPitch, wristRotate, claw, checkSum]
- To Science = [0x03, bigAct, smallAct, testTubeAct, drill, servoCam, checkSum]
### CAN
Teensy microcontrollers communicate with each other via CAN (Ebox, 2 Arm and 1 Science). ID of CAN msg sets priority, meaning ID=0x03 has to wait for ID=0x01 to finish sending messages on the bus
- To lowerArm: ID = 0x01
- To upperArm: ID = 0x02
- To Science: ID = 0x03
- Back to Ebox = 0x04
