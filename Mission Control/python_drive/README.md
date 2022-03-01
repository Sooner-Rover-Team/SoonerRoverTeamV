# manual_operate

This code can drive the rover, move the arm, and operate the science package.

## Usage

The config.ini file must have the correct ip addresses of the microcontrollers.

Ebox MBED IP: 10.0.0.101
Ebox MBED Port: 1001
Arm Arduino IP: 10.0.0.102
Arm Arduino Port: 1002
Science Arduino IP: 10.0.0.103
Science Arduino Port: 1003

The controller configuration can also be adjusted as different axes will have different indicies depending on the system/controller.
Config **0** sets the dual sticks to axes 0-3 while the triggers are 4 and 5. Config **1** sets left axes to 0 and 1 with the left trigger set to 2. The right stick is set to 3 and 4 with the right trigger at 5. To figure out the mappings of the controller, run controllertester.py.

## Controls

There are two distinct modes in the program: drive and operate. Drive obviously just drives the wheels. Operate can be used to control either the science package or the arm, depending on which is installed (can be toggled by pressing **Select**). **B** switches between drive and operate.

### Drive

The rover drives with tank controls (**Left Stick** moves left wheels, **Right Stick** moves right wheels). The **Left Bumper** will only move the front wheels while the **Right Bumper** will only move the back wheels. This could be useful for getting the rover unstuck. **A** will just make the lights flash. 

### Arm

The arm is controlled with the help of the GUI. The **Left Stick** controls the point of the wrist in space and the actuators will automatically adjust their length to keep the wrist on that point. The **Right Stick** controls the tilt and rotation of the wrist. The operator must be careful not to overtwist the wrist as the cords can get tangled and disconnected if the wrist is rotated too far. **A** opens and closes the claw. **Left Trigger** rotates the base to the left while **Right Trigger** rotates the base to the right.

### Science Package

The Science package has 4 distinct controllable elements. The **Left Stick** moves the drill up and down in space. The **Right Stick** controls the speed of the drill. **Right Trigger** increases the speed of the vacuum while **Left Trigger** decreases it. **Left Bumper** rotates the carousel clockwise while **Right Bumper** rotates the carousel counterclockwise. **A** attempts to move the carousel one seventh of a rotation, but it is based on time elapsed and may not move the same amout each time.
