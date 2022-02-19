import socket

def sendUDP(HOST,PORT,message): 
    #sends a message over UDP to a specific host and port
    BUFFERSIZE = 1024
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((HOST, PORT))
        s.sendall(message)

def sendWheelSpeeds(HOST, PORT, fl,ml,rl,fr,mr,rr):
    #sends a udp message containing the six different wheel speeds. 
    #arguments correspond to front left (fl), middle left (ml), etc.
    msg = bytearray(9)

    #start byte is the # character
    msg[0] = 0x23
    #byte to tell us what type of message it is.
    msg[1] = 0x00 #using hexadecimal since if the code changes, it will likely have to be in hex
    
    #Add the speeds to the message, while simultaneously summing them for the verification bit
    speeds = [fl,ml,rl,fr,mr,rr]
    # print(speeds)
    speeds = [int((x/90)+1)*126 for x in speeds]
    speeds[4] = 252-speeds[4]
    # print(speeds)
    cs = 0
    for i in range(6):
        msg[i + 2] = speeds[i]
        cs += speeds[i]

        #add verification bit
        msg[8] = int(bin(cs)[2:10], 2) #capped at 8 binary characters of length

    # print(msg)
    #send wheel speeds
    sendUDP(HOST,PORT,msg)

if __name__ == "__main__":
    speed = -90
    sendWheelSpeeds('127.0.0.1', 8080, speed, speed, speed, speed, speed, speed)
