#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EnsembleSocketConnection.py

Program creates class to interact with Ensemble controller (and thus AGR-75 
rotary stage) with an ASCII interface through a socket-based connection. 
This enables cross-platform use and no reliance on Aerotech 
dependencies/libraries.

Controller is assigned as server, PC is assigned as client. Wired connection
must be via Ethernet. For the program to work:
    
    -- Controller --
    (These tasks must be done in the Ensemble Configuration Manager, and so 
    must be done in Windows before moving to a different platform)
    1) In Parameters->System->ASCII change the following parameters:
	CommandSetup, enable Ethernet Socket 2
    2) In Parameters->System->Ethernet Sockets change the following:
	Socket2Port to 8000
	Socket2Setup to TCP server
    
    -- This file --
    1) Change the controller_ip to be the IP of the controller
    2) Change the controller_port to match Socket2Port specified above (8000)
    
Class has functionality specific to the SuperSpec project.

See Ensemble Help files for further documentation on the ASCII command 
interface and on AeroBasic commands.

@author: karimhalaseh
"""

import socket
import time
import sys

class Chopper:
    # the IP of the controller
    __controller_ip = ""
    # the port of the controller
    __controller_port = 8000
    # the socket that will be used to communicate
    __client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Parameters for motion
    ON_AXIS = "1"
    OFF_AXIS = "0"
    SPEED = "80"
    DWELL_TIME = 0.2
    # TODO: input these into string commands - test if there is a time penalty 
    # for doing so first though
    
    # ASCII controller response characters
    SUCCESS = "%"
    INVALID = "!"
    FAULT = "#"
    TIMEOUT = "$"


    # constructor opens socket to controller and enables motion 
    def __init__(self):
        
        try:
            self.__client_socket.connect(self.__controller_ip, 
                                         self.__controller_port)
            self.__client_socket.sendall("ENABLE A\n")
            response = self.__client_socket.recv(1)
            if (response == self.SUCCESS):
                print ("Connection successful\nMotion Enabled")
            else:
                print ("Error: code - ", response)
                # TODO: dictionary of response characters
            
            # SCurve controls curvature of velocity profile on % scale
            self.__client_socket.sendall("SCURVE 100\n")
            self.__client_socket.recv(1)
            
        except:
            print ("Error occurred: ", sys.exc_info()[0])
            print("Ensure controller is mapped and configured")
            
            
    # chops between on and off axis positions        
    def chop(self):
        while True:
            # chop to on-axis position of 1 deg
            self.__client_socket.sendall("MOVEABS A 1 F 80\n")
            self.__client_socket.recv(1)
            time.sleep(self.DWELL_TIME)
            # TODO: multithreading to not kill process during sleep
            
            # chop to off-axis position of 0 deg
            self.__client_socket.sendall("MOVEABS A 0 F 80\n")
            self.__client_socket.recv(1)
            time.sleep(self.DWELL_TIME)
    
    
    # moves to on axis position
    def on_axis(self):
        self.__client_socket.sendall("MOVEABS A 1 F 80\n")
        if (self.__client_socket.recv(1) == self.SUCCESS):
            print ("Chopper on-axis")
        
    
    # moves to off axis position
    def off_axis(self):
        self.__client_socket.sendall("MOVEABS A 0 F 80\n")
        if (self.__client_socket.recv(1) == self.SUCCESS):
            print ("Chopper off-axis")
    
    
    # disable motion and close socket
    def terminate(self):
        self.__client_socket.sendall("DISABLE A\n")
        if (self.__client_socket.recv(1) == self.SUCCESS):
            print ("Motion disabled")
        self.__client_socket.close()
    
    
    #TODO: increase overall error handling
    
        
        
    
    
    
