import math
import cv2
import mediapipe as mp
import socket
import time

Command = ["Forward", "Backward", "Right", "Left"]


class HandDetector:

    def connect_to_hc05(mac_address):
        try:
            # Create a Bluetooth socket
            sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

            # Connect to the HC-05 module using the provided MAC address and port number
            sock.connect((mac_address, 1))  # 1 is the port number, commonly used for Bluetooth serial communication

            print(f"Connected to {mac_address}")
            # Send data
            def sendData(Data):
                sock.send(Data.encode('utf-8'))
                print("Sent data")
                sock.close()

        except Exception as e:
            print(f"Error: {e}")

    

    def _init_(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5):

        self.staticMode = staticMode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.staticMode,
                                        max_num_hands=self.maxHands,
                                        model_complexity=modelComplexity,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)

        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

    def findHands(self, img, draw=True, flipType=True):
       
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                ## lmList
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)

                ## bbox
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                ## draw
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 0, 255), 2)
                    cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                                2, (255, 0, 255), 2)

        return allHands, img

    def fingersUp(self, myHand):
       
        fingers = []
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        if self.results.multi_hand_landmarks:

            # Thumb
            if myHandType == "Right":
                if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers


def main():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    width = 1280  
    height = 720

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
       
    detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)

    hc05_mac_address = 'FC:A8:9A:00:22:C8'
    try:
            # Create a Bluetooth socket
        sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

        # Connect to the HC-05 module using the provided MAC address and port number
        sock.connect((hc05_mac_address, 1))  # 1 is the port number, commonly used for Bluetooth serial communication

        print(f"Connected to {hc05_mac_address}")

        def sendData(Data):
            sock.send(Data.encode('utf-8'))
            print(Data)
            print("Sent data")

    except Exception as e:
        print(f"Error: {e}")

    while True:
        
        success, img = cap.read()

        hands, img = detector.findHands(img, draw=True, flipType=True)

        # Check if any hands are detected
        if hands:
            # Information for the first hand detected
            hand1 = hands[0]  # Get the first hand detected
            lmList1 = hand1["lmList"]  # List of 21 landmarks for the first hand
            bbox1 = hand1["bbox"]  # Bounding box around the first hand (x,y,w,h coordinates)
            center1 = hand1['center']  # Center coordinates of the first hand
            handType1 = hand1["type"]  # Type of the first hand ("Left" or "Right")

            # Count the number of fingers up for the first hand
            fingers1 = detector.fingersUp(hand1)
            
            if 'PreviousState' not in locals():
                PreviousState = fingers1
            # print(f'H1 = {fingers1.count(1)}', end=" ")  # Print the count of fingers that are up
            if(PreviousState != fingers1):
                    if (fingers1[1]==1 and fingers1[2]==0 and fingers1[3]==0 and fingers1[4]==0 and fingers1[0]==0):
                        CommandSend = Command[0] 
                        sendData("1")            
                    elif(fingers1[1]==1 and fingers1[2]==1 and fingers1[3]==0 and fingers1[4]==0 and fingers1[0]==0):
                        CommandSend = Command[1]
                        sendData("2")   
                    elif(fingers1[1]==1 and fingers1[2]==1 and fingers1[3]==1 and fingers1[4]==0 and fingers1[0]==0):
                        CommandSend = Command[2]
                        sendData("3")    
                    elif(fingers1[1]==1 and fingers1[2]==1 and fingers1[3]==1 and fingers1[4]==1 and fingers1[0]==0):
                        CommandSend = Command[3]
                        sendData("4")   
                    else:
                        fingers1= [0,0,0,0,0]
                        if PreviousState != fingers1:
                            sendData("0")
                    
                
            PreviousState = fingers1
            
            #print(" ")  # New line for better readability of the printed output

        # Display the image in a window
        cv2.imshow("Image", img)

        # Keep the window open and update it for each frame; wait for 1 millisecond between frames
        if cv2.waitKey(1) & 0xff == ord('q'):
            break
            sock.close()

if __name__ == "__main__":
    main()