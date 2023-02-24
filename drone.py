# Import the necessary modules
import socket
import threading
import os
# Start imports for CV
import time
import cv2
# End imports for CV
from colorama import Fore
import atexit

# IP and port of Tello
tello0_address = ('192.168.10.1', 8889)
# IP and port of local computer
local0_address = ('', 54874)
# Create a UDP connection that we'll send the command to
sock0 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to the local address and port
sock0.bind(local0_address)
# Global Variables
Victim_Found = False
routes = []

# path to save image
script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
rel_path = "/temp/image.png"
abs_file_path = script_dir + rel_path
temp_file_path = script_dir + "/temp/image1.png"
0
def receiveVid():
    global Victim_Found
    # Video Set Up
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111
    address_schema = 'udp://@{ip}:{port}'  # + '?overrun_nonfatal=1&fifo_size=5000'
    address = address_schema.format(ip=VS_UDP_IP, port=VS_UDP_PORT)
    qrDecoder = cv2.QRCodeDetector()

    # Retrieve data from Video Output
    cap = cv2.VideoCapture(address)
    if not cap.isOpened():
        cap.open(address)
    start = time.time()
    while time.time() - start < 3:
        print(Fore.WHITE + 'trying to grab a frame...')
        grabbed, frame = cap.read()
        if frame is not None:
            break
    if not grabbed or frame is None:
        raise Exception('Failed to grab first frame from video stream')

    if grabbed:
        delay_detact = 0
        while not Victim_Found:
            grabbed, frame = cap.read()
            # Modify Frame Image
            crop_Img = frame[0:240, 0:960]
            resized_image = cv2.resize(crop_Img, (720, 720), interpolation = cv2.INTER_AREA)
            dark_Img = cv2.convertScaleAbs(resized_image, 0, 0.75) # alpha 0<1 contrast. Beta: Brightness -> -127 to 127
            # Decode Image
            if delay_detact < 3:
                cv2.imshow("Results", resized_image)
                delay_detact += 1
            else:
                try:
                    data, bbox, rectifiedImage = qrDecoder.detectAndDecode(resized_image)
                    data1, bbox1, rectifiedImage1 = qrDecoder.detectAndDecode(dark_Img)
                    pass
                except:
                    print(Fore.RED + "Error Ignored for QRCode detection")
                    # Check if QR Code is Identified
                if len(data) > 0 or len(data1) > 0:
                    if len(data) > 0:
                        print(Fore.LIGHTGREEN_EX + "Decoded Data : {}".format(data))
                        cv2.imshow("Results", resized_image)
                        cv2.imwrite(temp_file_path, resized_image)
                    else:
                        print(Fore.LIGHTGREEN_EX + "Decoded Dark Data : {}".format(data1))
                        cv2.imshow("Results", dark_Img)
                        cv2.imwrite(temp_file_path, dark_Img)
                    Victim_Found = True
                    while routes:
                        routes.pop(0)
                    send("stop", 5)
                    # send("back 20", 10)
                    send("land", 2)
                    print(Fore.GREEN + "Victim Found")
                    exit()
                else:
                    # print(Fore.MAGENTA + "QR Code not detected")
                    cv2.imshow("Results", resized_image)
                delay_detact = 0
            cv2.waitKey(1)
            # cv2.destroyAllWindows()

# Receive the message from Tello
def receive():
    # Continuously loop and listen for incoming messages
    while True:
        # Try to receive the message otherwise print the exception
        try:
            response0, ip_address = sock0.recvfrom(128)
            print(Fore.CYAN + "Receive message: Tello #0: " + str(response0.decode(encoding='utf-8')))
        except Exception as e:
            sock0.close()
            print("Error receiving: " + str(e))
            break

# Send the message to All Tello and allow for a delay in seconds
commandSequence = 0
def send(message, delay):
    try:
        sock0.sendto(message.encode(), tello0_address)
        print(Fore.WHITE + "(" + str(commandSequence) + ")" + "Sending message: " + message)
    except Exception as e:
        print(Fore.RED + "Error sending: " + str(e))
    # Delay for a user-defined period of time
    time.sleep(delay)

def exit_handler():
    while routes:
        routes.pop(0)
    send("battery?", 3)
    exit()


# ====================     Start Code      ====================
# Create and start a listening thread that runs in the background
receiveThread = threading.Thread(target=receive)
receiveThread.daemon = True
receiveThread.start()
receiveVidThread = threading.Thread(target=receiveVid)
receiveVidThread.daemon = True
receiveVidThread.start()
atexit.register(exit_handler)

# Compress Route to Array
with open('route.txt') as f:
    for line in f.readlines():
        routeAndDelay = line.split(",")
        routeAndDelay[1] = routeAndDelay[1].replace('\n', '')
        routes.append(routeAndDelay)
        print(routes)

# Set Up Tello
send("command", 1)
send("downvision 1",1)
send("streamon",1)
send("speed 100",1)
send("battery?", 1)
send("takeoff", 8)

# Start Flight
for route in routes:
    telloDelay = route[1]
    if not Victim_Found:
        commandSequence = commandSequence + 1
        send(route[0], int(telloDelay))
# End Flight

if Victim_Found:
    time.sleep(50)
send("battery?", 3)
print("Mission completed successfully!")

# Close the socket
sock0.close()