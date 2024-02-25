import socket
import matplotlib.pyplot as plt
from collections import deque
from datetime import datetime
import select

# Set the IP address and port to bind the UDP server
UDP_IP = "192.168.1.4"  # Your local IP address
UDP_PORT = 1255

# data=b'\x14\x16\x03\xfd'

# Decode the received data assuming it is in UTF-8 encoding
# sensor_values = [byte for byte in data]
# print(sensor_values)

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the specified IP address and port
sock.connect((UDP_IP, UDP_PORT))

print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")
sock.sendall(bytearray([0]))
# Initialize variables for peak detection
peak_threshold = 10  # Adjust as needed
peaks = []

# Initialize the plots
plt.ion()  # Turn on interactive mode
fig, axs = plt.subplots(3, 1, figsize=(10, 10))
plt.subplots_adjust(hspace=0.5)


# Initialize deque buffers for each plot
buffers = [deque(maxlen=20) for _ in range(3)]
lines = []
labels = ['Temperature (C)', 'Humidity (%)', 'Methane (ppm)']
# 82 - 94 F in Utah day time temp
ylims = [(10, 40), (0, 100), (0, 1023)]
# Initialize plots
for i, ax in enumerate(axs):
    line, = ax.plot([], [], marker='o', linestyle='-', label=f'Sensor {i+1}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel(f'{labels[i]}')
    ax.set_title(f'Live {labels[i]} Sensor  Plot')
    ax.set_ylim(ylims[i][0], ylims[i][1])  # Assuming sensor readings are in the range 0-1023
    ax.legend(loc='upper left')
    lines.append(line)



# Update the plots with new data
def update_plots(x, ys):
    for i, y in enumerate(ys):
        buffers[i].append(y)
        lines[i].set_xdata(range(1, len(buffers[i]) + 1))  # Use a continuous range for x-axis
        lines[i].set_ydata(buffers[i])
        axs[i].relim()
        axs[i].autoscale_view()
    fig.canvas.flush_events()

try:
    while True:
        # Receive data and address from the client
        # ready_to_read, ready_to_write, exceptional_conditions = select.select([sock], [], [], 0)  # Number = timeout, 0 -> "nonblocking"
        # try:
        #     data = sock.recv(1024)
        #     if data:
        #         print("Received message:", data)
        #     else:
        #         print("No data received")
        # except socket.error as e:
        #     print("Socket error:", e)
        data = sock.recvfrom(1024)        # print([byte for byte in data])
        # if sock in ready_to_read:
        #     try:
        #         data = sock.recvfrom(1024)
        #         print([byte for byte in data])
        #         # print(encodermsg)
        #         # encoderprint = encodermsg[1] * 255 + encodermsg[0]
        #         # print(encoderprint)

        #     except socket.timeout:
        #         print("Socket timeout")
        #         # continue
        # else:
        #     print("Not ready")
        #     continue
        # print(data)
        # data=b'\x14\x16\x03\xfd'

        # Decode the received data assuming it is in UTF-8 encoding
        sensor_values = [byte for byte in data[0]]
        # print(sensor_values)

        # Convert the received data to a list of floats
        # sensor_values = [float(value) for value in message.split(',')]

        # Update the plots with the new sensor values
        sensor_values = [sensor_values[0], sensor_values[1], sensor_values[2] * 256 + sensor_values[3]]
        print(f"Received message: {sensor_values}")
        update_plots(len(buffers[0]) + 1, sensor_values)  # Increment the x-axis index

        # Check for peaks
        if max(sensor_values) > peak_threshold:
            peaks.append((datetime.now(), i + 1, sensor_values))  # Store timestamp, sensor index, and value of peak

except KeyboardInterrupt:
    print("Plotting stopped.")
    # Save peaks to a file
    with open("peak_data.txt", "w") as f:
        f.write("Sensor Peak Ratings\n")
        for peak in peaks:
            f.write(f"{peak[0]}, Sensor {peak[1]}, {peak[2]}\n")

# except Exception as e:
#     # Save peaks to a file before exiting
#     print("An error occurred:", e)
#     with open("peak_data.txt", "w") as f:
#         for peak in peaks:
#             f.write(f"{peak[0]}, Sensor {peak[1]}, {peak[2]}\n")
finally:
    plt.ioff()  # Turn off interactive mode
    plt.show()
    sock.close()

# import socket
# import matplotlib.pyplot as plt
# from collections import deque
# from datetime import datetime
# import select
# import threading

# class ScienceSensorPlots:
#     def __init__(self, sock):

#         self.socket = sock#socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         self.peak_threshold = 10
#         self.peaks = []
#         self.buffers = [deque(maxlen=20) for _ in range(3)]
#         self.labels = ['Temperature (C)', 'Humidity (%)', 'Methane (ppm)']
#         self.lines = []
#         self.fig, self.axs = plt.subplots(3, 1, figsize=(10, 10))
#         plt.subplots_adjust(hspace=0.3)
#         for i, ax in enumerate(self.axs):
#             line, = ax.plot([], [], marker='o', linestyle='-', label=f'Sensor {i+1}')
#             ax.set_xlabel('Time (s)')
#             ax.set_ylabel(f'{self.labels[i]}')
#             ax.set_title(f'Live {self.labels[i]} Sensor Plot')
#             ax.set_ylim(0, 1023)
#             ax.legend(loc='upper left')
#             self.lines.append(line)
#         self.thread = threading.Thread(target=self.run)

#     def update_plots(self, x, ys):
#         for i, y in enumerate(ys):
#             self.buffers[i].append(y)
#             self.lines[i].set_xdata(range(1, len(self.buffers[i]) + 1))
#             self.lines[i].set_ydata(self.buffers[i])
#             self.axs[i].relim()
#             self.axs[i].autoscale_view()
#         self.fig.canvas.flush_events()

#     def run(self):
#         # print(f"UDP server listening on {self.udp_ip}:{self.udp_port}")
#         try:
#             self.socket.connect((self.udp_ip, self.udp_port))
#             while True:
#                 ready_to_read, ready_to_write, exceptional_conditions = select.select([self.socket], [], [], 0)

#                 if self.socket in ready_to_read:
#                     try:
#                         data = self.socket.recv(1024)
#                     except socket.timeout:
#                         print("Socket timeout")
#                         continue
#                 else:
#                     continue

#                 message = data.decode("utf-8")
#                 sensor_values = [float(value) for value in message.split(',')]
#                 sensor_values = [sensor_values[0], sensor_values[1], sensor_values[2] * 256 + sensor_values[3]]
#                 print(f"Received message: {sensor_values}")
#                 self.update_plots(len(self.buffers[0]) + 1, sensor_values)

#                 if max(sensor_values) > self.peak_threshold:
#                     self.peaks.append((datetime.now(), i + 1, sensor_values))
#         except KeyboardInterrupt:
#             print("Plotting stopped.")
#             with open("peak_data.txt", "w") as f:
#                 f.write("Sensor Peak Ratings\n")
#                 for peak in self.peaks:
#                     f.write(f"{peak[0]}, Sensor {peak[1]}, {peak[2]}\n")
#         except Exception as e:
#             print("An error occurred:", e)
#             with open("peak_data.txt", "w") as f:
#                 for peak in self.peaks:
#                     f.write(f"{peak[0]}, Sensor {peak[1]}, {peak[2]}\n")
#         finally:
#             plt.ioff()
#             plt.show()
#             self.socket.close()
    
#     def start(self):
#         self.thread.start()

# # # Set the IP address and port to bind the UDP server
# UDP_IP = "192.168.1.101"  # Your local IP address
# UDP_PORT = 1001
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.connect((UDP_IP, UDP_PORT))

# # Create an instance of UDPSensorPlotter and start the thread
# udp_sensor_plotter = ScienceSensorPlots(sock)
# udp_sensor_plotter.start()
