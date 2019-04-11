"""
Program creates class to interact with Ensemble controller (and thus AGR-75
rotary stage) with an ASCII interface through a socket-based connection. 
Functionality specific to SuperSpec.

Controller is assigned as server, PC is assigned as client.
For the program to work:
    
    -- Controller --
    (These tasks must be done in the Ensemble Configuration Manager, and so 
    must be done in Windows before moving to a different platform)
    1) In Parameters->System->Communication->ASCII change the following
    parameters:
    CommandSetup, enable Ethernet Socket 2
    2) In Parameters->System->Communication->Ethernet Sockets change
    the following:
    Socket2Port to 8000
    Socket2Setup to TCP server
    
    -- This file --
    1) Change the controller_ip to be the IP of the controller
    2) Change the controller_port to match Socket2Port specified above (8000)

See Ensemble Help files for further documentation on the ASCII command 
interface and on AeroBasic commands.
"""

import socket
import time
import sys


class Chopper:
    __controller_ip = "192.168.1.16"
    __controller_port = 8000
    __client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    DATA_BUFFER = 4096  # ASCII interface acknowledges command with a char
    RESPONSE_DICT = {'%': 'Success', '!': 'Invalid command',
                     '#': 'Axis at fault', '$': 'Command timed out'}

    # open socket to controller and enable motion
    def __init__(self):
        try:
            self.__client_socket.connect((self.__controller_ip,
                                         self.__controller_port))
            # message encoding required for Python 3, not Python 2
            self.__client_socket.sendall("ENABLE A\n".encode())
            response = self.RESPONSE_DICT.get(self.__client_socket.recv(
                self.DATA_BUFFER).decode()[0])
            if response == 'Success':
                print("Connection successful\nMotion Enabled")
            else:
                print(response)
        except:
            print("Error occurred: ", sys.exc_info()[0])
            print("Ensure controller is mapped and configured")

    # chop between on and off axis positions
    def chop(self, on_axis='1', off_axis='0', speed='80', dwell_time=0.2):
        # WARNING - no command checking done to minimize latency
        # Use on-axis() and off-axis() to check if errors occur
        while True:
            try:
                self.__client_socket.sendall(("MOVEABS A " + on_axis + " F "
                                              + speed + "\n").encode())
                self.__client_socket.recv(self.DATA_BUFFER)
                time.sleep(dwell_time)

                self.__client_socket.sendall(("MOVEABS A " + off_axis + " F "
                                              + speed + "\n").encode())
                self.__client_socket.recv(self.DATA_BUFFER)
                time.sleep(dwell_time)
            except KeyboardInterrupt:
                self.stop()
                break  # user interrupt (Ctrl-C) without closing socket

    # move to on axis position
    def on_axis(self, pos='1', speed='80'):
        self.__client_socket.sendall(("MOVEABS A " + pos + " F "
                                      + speed + "\n").encode())
        response = self.RESPONSE_DICT.get(self.__client_socket.recv(
            self.DATA_BUFFER).decode()[0])
        if response != 'Success':
            print(response)

    # move to off axis position
    def off_axis(self, pos='0', speed='80'):
        self.__client_socket.sendall(("MOVEABS A " + pos + " F "
                                      + speed + "\n").encode())
        response = self.RESPONSE_DICT.get(self.__client_socket.recv(
            self.DATA_BUFFER).decode()[0])
        if response != 'Success':
            print(response)

    # abort motion
    def stop(self):
        self.__client_socket.sendall("ABORT A\n".encode())
        response = self.RESPONSE_DICT.get(self.__client_socket.recv(
            self.DATA_BUFFER).decode()[0])
        if response != 'Success':
            print(response)

    # disable motion and close socket
    def terminate(self):
        self.__client_socket.sendall("DISABLE A\n".encode())
        response = self.RESPONSE_DICT.get(self.__client_socket.recv(
            self.DATA_BUFFER).decode()[0])
        if response == 'Success':
            print("Motion disabled")
        else:
            print(response)
        self.__client_socket.close()