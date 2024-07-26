import numpy as np
import cv2
import imutils
import time
from tkinter import *
from collections import deque
from imutils.video import VideoStream
import colorsys
import threading
import serial


serial_port = "COM4"
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate, timeout=100)

def update_values():
    global greenLower, greenUpper
    greenLower = (sliderH_Down.get(), sliderS_Down.get(), sliderV_Down.get())
    greenUpper = (sliderH_Up.get(), sliderS_Up.get(), sliderV_Up.get())
    update_color_preview()
    master.after(100, update_values)

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h/255.0, s/255.0, v/255.0)
    return int(r * 255), int(g * 255), int(b * 255)

def update_color_preview():
    lower_color = hsv_to_rgb(sliderH_Down.get(), sliderS_Down.get(), sliderV_Down.get())
    upper_color = hsv_to_rgb(sliderH_Up.get(), sliderS_Up.get(), sliderV_Up.get())
    lower_color_hex = f'#{lower_color[0]:02x}{lower_color[1]:02x}{lower_color[2]:02x}'
    upper_color_hex = f'#{upper_color[0]:02x}{upper_color[1]:02x}{upper_color[2]:02x}'
    canvas_lower.config(bg=lower_color_hex)
    canvas_upper.config(bg=upper_color_hex)

def video_thread():
    global vs, greenLower, greenUpper, pts

    # define the lower and upper boundaries of the "green" ball in the HSV color space, then initialize the list of tracked points
    greenLower = (29, 86, 6)
    greenUpper = (64, 255, 255)

    # initialize the list of tracked points, the frame counter, and the coordinate deltas
    pts = deque(maxlen=32)
    counter = 0
    (dX, dY) = (0, 0)

    # to the webcam
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    while True:
        # grab the current frame
        frame = vs.read()
        # handle the frame from VideoCapture or VideoStream
        # if we are viewing a video and we did not grab a frame, then we have reached the end of the video
        if frame is None:
            break
        # resize the frame, blur it, and convert it to the HSV color space
        frame = imutils.resize(frame, width=600)
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        # construct a mask for the color "green", then perform a series of dilations and erosions to remove any small blobs left in the mask
        mask = cv2.inRange(hsv, greenLower, greenUpper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        # find contours in the mask and initialize the current (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None
        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame, then update the list of tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                #pos = center[0]
                #pos = int(pos)
                #pos = (pos + 1)/3.3
                #print(int(pos))
                #ser.write(str(int(pos)) + ",")
                #ser.write(",") #need investigation, i down why but i think not work for codec, i need info why dont working
        # update the points queue
        pts.appendleft(center)
        # loop over the set of tracked points
        for i in range(1, len(pts)):
            # if either of the tracked points are None, ignore them
            if pts[i - 1] is None or pts[i] is None:
                continue
            # otherwise, compute the thickness of the line and draw the connecting lines
            thickness = int(np.sqrt(32 / float(i + 1)) * 2.5)
            cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        # show the frame to our screen
        cv2.imshow("Frame", frame)
        cv2.imshow("Mask", mask)
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break

    vs.stop()
    cv2.destroyAllWindows()

master = Tk()
master.title("HSV Sliders")

Label(master, text="Hue Upper").pack()
sliderH_Up = Scale(master, from_=0, to=255, orient=HORIZONTAL)
sliderH_Up.set(64)
sliderH_Up.pack()

Label(master, text="Saturation Upper").pack()
sliderS_Up = Scale(master, from_=0, to=255, orient=HORIZONTAL)
sliderS_Up.set(255)
sliderS_Up.pack()

Label(master, text="Value Upper").pack()
sliderV_Up = Scale(master, from_=0, to=255, orient=HORIZONTAL)
sliderV_Up.set(255)
sliderV_Up.pack()

Label(master, text="Hue Lower").pack()
sliderH_Down = Scale(master, from_=0, to=255, orient=HORIZONTAL)
sliderH_Down.set(29)
sliderH_Down.pack()

Label(master, text="Saturation Lower").pack()
sliderS_Down = Scale(master, from_=0, to=255, orient=HORIZONTAL)
sliderS_Down.set(86)
sliderS_Down.pack()

Label(master, text="Value Lower").pack()
sliderV_Down = Scale(master, from_=0, to=255, orient=HORIZONTAL)
sliderV_Down.set(6)
sliderV_Down.pack()

Label(master, text="Lower Color Preview").pack()
canvas_lower = Canvas(master, width=100, height=50, bg="#000000")
canvas_lower.pack()

Label(master, text="Upper Color Preview").pack()
canvas_upper = Canvas(master, width=100, height=50, bg="#000000")
canvas_upper.pack()

# Start the video thread
video_thread = threading.Thread(target=video_thread)
video_thread.start()

update_values()

master.mainloop()
