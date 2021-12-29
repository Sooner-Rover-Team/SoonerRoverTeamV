from drive import sendWheelSpeeds

HOST = '127.0.0.1' 
# 127.0.0.1 is the 'loopback' address, or the address
# of your own computer

PORT = 2000 
# this number is arbitrary as long as it is above 1024

sendWheelSpeeds(HOST, PORT, 255, 255, 255, 255, 255, 255)
# the six arguments represent each wheels speed (on a scale between 0 and 255, since it will be stored in a byte).
# the order of the wheels in the arguments is Front Left, Middle Left, Rear Left, Front Right, Middle Right, and Rear Right. 
# sendWheelSpeeds(HOST, PORT, fl, ml, rl, rt, mr, rr)