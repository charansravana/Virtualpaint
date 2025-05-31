# import cv2
# import numpy as np
# import os
# import HandTrackingModule as htm

# brushThickness = 15
# eraserThickness = 50

# folderPath = "Header"
# overlayList = [cv2.imread(os.path.join(folderPath, f)) for f in sorted(os.listdir(folderPath))]
# header = overlayList[0]

# drawColor = (255, 0, 255)
# xp, yp = 0, 0
# imgCanvas = np.zeros((720, 1280, 3), np.uint8)

# cap = cv2.VideoCapture(0)
# cap.set(3, 1280)
# cap.set(4, 720)

# detector = htm.handDetector(detectionCon=0.85)

# while True:
#     success, img = cap.read()
#     img = cv2.flip(img, 1)
#     img = detector.findHands(img)
#     lmList = detector.findPosition(img)

#     if lmList:
#         x1, y1 = lmList[8][1:]  # Index
#         x2, y2 = lmList[12][1:]  # Middle

#         fingers = detector.fingersUp()

#         if fingers[1] and fingers[2]:
#             xp, yp = 0, 0
#             if y1 < 125:
#                 if 250 < x1 < 450:
#                     header = overlayList[0]
#                     drawColor = (255, 0, 255)
#                 elif 550 < x1 < 750:
#                     header = overlayList[1]
#                     drawColor = (255, 0, 0)
#                 elif 800 < x1 < 950:
#                     header = overlayList[2]
#                     drawColor = (0, 255, 0)
#                 elif 1050 < x1 < 1200:
#                     header = overlayList[3]
#                     drawColor = (0, 0, 0)
#             cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

#         elif fingers[1] and not fingers[2]:
#             cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
#             if xp == 0 and yp == 0:
#                 xp, yp = x1, y1

#             thickness = eraserThickness if drawColor == (0, 0, 0) else brushThickness
#             cv2.line(img, (xp, yp), (x1, y1), drawColor, thickness)
#             cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, thickness)
#             xp, yp = x1, y1

#     imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
#     _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
#     imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
#     img = cv2.bitwise_and(img, imgInv)
#     img = cv2.bitwise_or(img, imgCanvas)

#     img[0:125, 0:1280] = header
#     cv2.imshow("Image", img)
#     cv2.imshow("Canvas", imgCanvas)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()



import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

brushThickness = 15
eraserThickness = 100

folderPath = "Header"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    image = cv2.resize(image, (640, 126))
    overlayList.append(image)
print(len(overlayList))
header = overlayList[0]
#print(overlayList[0])
drawColor = (255, 0, 255)

cap = cv2.VideoCapture(0)
print(cap.get(3))
print(cap.get(4))
cap.set(3, 1280)
cap.set(4, 720)
print(cap.get(3))
print(cap.get(4))

detector = htm.handDetector(detectionCon=1,maxHands=1)

xp, yp = 0, 0
imgCanvas = np.zeros((480, 640, 3), np.uint8)

while True:

    # 1. Import image
    success, img = cap.read()
    
    img = cv2.flip(img, 1)

    # # 2. Find Hand Landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:

         # print(lmList)
 
         # tip of index and middle fingers
         x1, y1 = lmList[8][1:]
         x2, y2 = lmList[12][1:]
 
         # 3. Check which fingers are up
         fingers = detector.fingersUp()
         #print(fingers)
 
        # 4. If Selection Mode - Two finger are up
         if fingers[1] and fingers[2]:
            # xp, yp = 0, 0
            print("Selection Mode")
            # Checking for the click
            if y1 < 126:
                if 100 < x1 < 220:
                    header = overlayList[0]
                    drawColor = (255, 255, 0)
                elif 250 < x1 < 350:
                    header = overlayList[1]
                    drawColor = (135,206,235)
                elif 380 < x1 < 500:
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                elif 520 < x1 < 640:
                    header = overlayList[3]
                    drawColor = (0, 0, 0)
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
 
        # 5. If Drawing Mode - Index finger is up
         if fingers[1] and fingers[2] == False:
            cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
            print("Drawing Mode")
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
            cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)


            xp, yp = x1, y1

        # Clear Canvas when all fingers are up
         if all (x >= 1 for x in fingers):
            imgCanvas = np.zeros((480, 640, 3), np.uint8)

    # Setting the header image
    img[0:126, 0:640] = header
    imgCanvas = cv2.resize(imgCanvas, (img.shape[1], img.shape[0]))
    img = cv2.addWeighted(img,0.5,imgCanvas,0.5,0)
    cv2.imshow("Image", img)
    #cv2.imshow("Canvas", imgCanvas)
    #cv2.imshow("Inv", imgInv)
    cv2.waitKey(1)
    
cap.release()   # stop capturing the image/video
cv2.destroyAllWindows()