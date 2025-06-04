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
import pygame

# Initialize pygame mixer for sound effects with dummy audio driver fallback
import os
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.mixer.init()

# Placeholder sound effects using simple beep sounds
def play_beep():
    duration = 100  # milliseconds
    freq = 440  # Hz
    try:
        import winsound
        winsound.Beep(freq, duration)
    except ImportError:
        # For non-Windows, use pygame beep alternative
        pygame.mixer.Sound(buffer=pygame.sndarray.make_sound(
            pygame.sndarray.array([4096 * (i % 2 * 2 - 1) for i in range(44100)]))).play()

class DummySound:
    def play(self):
        play_beep()

sound_color_change = DummySound()
sound_draw_start = DummySound()
sound_draw_stop = DummySound()
sound_clear = DummySound()
sound_save = DummySound()

brushThickness = 15
eraserThickness = 100

folderPath = "Header"
myList = os.listdir(folderPath)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    image = cv2.resize(image, (640, 126))
    overlayList.append(image)
header = overlayList[0]

drawColor = (255, 0, 255)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam. Please ensure a webcam is connected and accessible.")
    exit(1)

detector = htm.handDetector(detectionCon=1, maxHands=2)

xp, yp = 0, 0
imgCanvas = np.zeros((480, 640, 3), np.uint8)

# Variables for undo functionality
undo_stack = []

# Brush size options
brush_sizes = [5, 10, 15, 20, 25]
current_brush_index = 2  # default brush size index

def save_canvas(img):
    filename = f'drawing_{int(time.time())}.png'
    cv2.imwrite(filename, img)
    sound_save.play()
    print(f"Canvas saved as {filename}")

def clear_canvas():
    global imgCanvas, undo_stack
    undo_stack.append(imgCanvas.copy())
    imgCanvas = np.zeros((480, 640, 3), np.uint8)
    sound_clear.play()

def undo():
    global imgCanvas, undo_stack
    if undo_stack:
        imgCanvas = undo_stack.pop()
        print("Undo performed")

def draw_buttons(img):
    # Draw clear button
    cv2.rectangle(img, (10, 10), (110, 60), (0, 0, 255), -1)
    cv2.putText(img, 'Clear', (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw save button
    cv2.rectangle(img, (120, 10), (220, 60), (0, 255, 0), -1)
    cv2.putText(img, 'Save', (140, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw undo button
    cv2.rectangle(img, (230, 10), (330, 60), (255, 0, 0), -1)
    cv2.putText(img, 'Undo', (250, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Draw brush size buttons
    for i, size in enumerate(brush_sizes):
        color = (255, 255, 255)
        if i == current_brush_index:
            color = (0, 255, 255)
        cv2.circle(img, (400 + i*50, 35), size, color, -1)

def check_button_click(x, y):
    global drawColor, header, current_brush_index
    if 10 < x < 110 and 10 < y < 60:
        clear_canvas()
        return True
    elif 120 < x < 220 and 10 < y < 60:
        save_canvas(imgCanvas)
        return True
    elif 230 < x < 330 and 10 < y < 60:
        undo()
        return True
    elif 375 < x < 625 and 10 < y < 60:
        for i in range(len(brush_sizes)):
            if 400 + i*50 - brush_sizes[i] < x < 400 + i*50 + brush_sizes[i]:
                current_brush_index = i
                sound_color_change.play()
                return True
    return False

drawing = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    draw_buttons(img)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        fingers = detector.fingersUp()

        if fingers[1] and fingers[2]:
            drawing = False
            if y1 < 126:
                if 100 < x1 < 220:
                    header = overlayList[0]
                    drawColor = (255, 255, 0)
                    sound_color_change.play()
                elif 250 < x1 < 350:
                    header = overlayList[1]
                    drawColor = (135, 206, 235)
                    sound_color_change.play()
                elif 380 < x1 < 500:
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                    sound_color_change.play()
                elif 520 < x1 < 640:
                    header = overlayList[3]
                    drawColor = (0, 0, 0)
                    sound_color_change.play()
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        elif fingers[1] and not fingers[2]:
            if check_button_click(x1, y1):
                pass
            else:
                cv2.circle(img, (x1, y1), brush_sizes[current_brush_index], drawColor, cv2.FILLED)
                if not drawing:
                    sound_draw_start.play()
                    drawing = True
                    xp, yp = x1, y1
                    undo_stack.append(imgCanvas.copy())
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brush_sizes[current_brush_index])
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brush_sizes[current_brush_index])
                xp, yp = x1, y1

        else:
            if drawing:
                sound_draw_stop.play()
            drawing = False

        if all(x >= 1 for x in fingers):
            clear_canvas()

    img[0:126, 0:640] = header
    imgCanvas = cv2.resize(imgCanvas, (img.shape[1], img.shape[0]))
    img = cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)

    cv2.imshow("Image", img)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
