import numpy as np
import face_recognition
import cv2
import os

from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import sys
from time import sleep
import requests
import time

def send_safety_check():
    r = requests.post("https://415848bd.ngrok.io/sms", \
	data={'command': 'check_safety'})
    print('send check')

key_image_name = 'dataset/yuanwei.jpg'
key_image = cv2.imread(key_image_name)
# key_image = cv2.resize(key_image, (0, 0), fx=0.3, fy=0.3)
known_small_frame = key_image[:, :, ::-1]

# Find all the faces and face encodings in the current frame of video
known_face_locations = face_recognition.face_locations(known_small_frame)
known_face_encodings = face_recognition.face_encodings(known_small_frame, known_face_locations)
####################

# Set up camera constants
# MAX is 1280
IM_WIDTH = 640

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

# Initialize Picamera and grab reference to the raw capture
camera = PiCamera()
camera.resolution = (IM_WIDTH, IM_WIDTH)
camera.framerate = 5
rawCapture = PiRGBArray(camera, size=(IM_WIDTH, IM_WIDTH))
rawCapture.truncate(0)

cnt = 0

def add_content_to_frame(frame, face_locations, face_names):
    # Display the results
    for i in range(len(face_locations)):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top = int(face_locations[i][0])
        right = int(face_locations[i][1])
        bottom = int(face_locations[i][2])
        left = int(face_locations[i][3])

        # Draw a label with a name below the face
        pts = np.array([[left, top],
                        [left, bottom],
                        [right, bottom],
                        [right, top]],
                       np.int32)
        
        cv2.polylines(frame, [pts], True, (0, 255, 0))

        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, face_names[i], (left, top - 6), font, 1.0, (0, 255, 0), 1)

face_names = ['']
try:
    for frame1 in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = frame1.array
        cnt += 1
        
        frame = frame[:, :, ::-1].copy()
        face_locations = face_recognition.face_locations(frame)

        if cnt >= 10:
            cnt = 0
           
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                name = "Unknown"
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, 0.5)
                if True in matches:
                    name = "yuanwei"
                face_names.append(name)
            print(face_names)
            
            if "Unknown" in face_names:
                send_safety_check()
                
            r = requests.post("https://415848bd.ngrok.io/safe")
            print(r.status_code, r.reason)
            print(r.text[:300] + '...')
            if r.text == 'False':
                current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                r = requests.post("https://415848bd.ngrok.io/sms", \
                    data={'command': 'update', \
                          'Localization': 'Latitude： 47.606209, longitude: -122.332069', \
                          'time': current_time})
        if len(face_locations) >= 1:
            add_content_to_frame(frame, face_locations, face_names)
        # frame.setflags(write=1)
        cv2.imshow('Object detector', frame)
        cv2.waitKey(1)
        rawCapture.truncate(0)
except KeyboardInterrupt:
    camera.close()
    cv2.destroyAllWindows()

