

""" SEND UDP MESSAGES """
# import socket
# import time
# port = 3333 # port of host for server
# ip = "192.168.0.246" #"192.168.0.2" # ip of host for server
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# s.connect((ip,port))
# print("waiting on port:", port)
# while 1:
#     # sendData = [255] # sendData can be any length. 255 would be an ID for arm or something
#     # userInput = 1 #int(input("Enter a value to send"))    
#     # sendData.append(userInput)
#     # sendData.append(userInput+1)
#     # #s.sendto(sendData.encode('utf-8'), (ip, port))
#     # #print("\n\n 1. Client Sent : ", sendData, "\n\n")
    
#     # s.sendall(bytearray(sendData)) # sends msg through socket
#     # print("message sent...")
#     # time.sleep(1)
# s.close()


""" RECEIVE UDP MESSAGES """
# import socket

# # Set the IP address and port to bind the UDP server
# UDP_IP = "0.0.0.0"  # 0.0.0.0 means the server will listen on all available interfaces
# UDP_PORT = 3333  # Replace with the port number

# # Create a UDP socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Bind the socket to the specified IP address and port
# sock.bind((UDP_IP, UDP_PORT))

# print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")

# while True:
#     # Receive data and address from the client
#     data, addr = sock.recvfrom(1024)  # 1024 is the buffer size

#     # Decode the received data assuming it is in UTF-8 encoding
#     message = data.decode("utf-8")

#     print(f"Received message from {addr}: {message}")


""" RECEIVE AND PLOT UDP MESSAGES """
import socket
import matplotlib.pyplot as plt
import select
from collections import deque

# Set the IP address and port to bind the UDP server
UDP_IP = "0.0.0.0" # sender should connect to receiver, so make this ur ip
UDP_PORT = 3333

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the specified IP address and port
sock.bind((UDP_IP, UDP_PORT))

print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")
size = 20
# Initialize the plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()
x_data, y_data = deque(maxlen=size), deque(maxlen=size)  # Use deque to keep a fixed-size buffer
line, = ax.plot(x_data, y_data, marker='o', linestyle='-', color='b', label='Sensor Data')
ax.set_xlabel('Time (s)')
ax.set_ylabel('Current (A)')
ax.set_title('Live Current Data Plot')

# Add legend
ax.legend(loc='upper left')

# Update the plot with new data
def update_plot(x, y):
    x_data.append(x)
    y_data.append(y)
    line.set_xdata(range(1, len(x_data) + 1))  # Use a continuous range for x-axis
    line.set_ydata(y_data)
    ax.relim()
    ax.autoscale_view()
    fig.canvas.flush_events()

try:
    while True:
        ready_to_read, ready_to_write, exceptional_conditions = select.select([sock], [], [], 0)  # Number = timeout, 0 -> "nonblocking"
        if sock in ready_to_read:
            try:
                data = sock.recv(1024)

                message = data.decode("utf-8")

                sensor_value = float(message)

                print(f"Received message from {addr}: {sensor_value}")

                update_plot(len(x_data) + 1, sensor_value)


            except socket.timeout:
                print("Socket timeout")
        # Receive data and address from the client
        data, addr = sock.recvfrom(1024)

        # Decode the received data assuming it is in UTF-8 encoding
        message = data.decode("utf-8")

        # Convert the received data to a float (replace this with your actual conversion logic)
        sensor_value = float(message)

        print(f"Received message from {addr}: {sensor_value}")

        # Update the plot with the new sensor value
        update_plot(len(x_data) + 1, sensor_value)  # Increment the x-axis index

except KeyboardInterrupt:
    print("Plotting stopped.")
finally:
    plt.ioff()  # Turn off interactive mode
    plt.show()
    sock.close()


