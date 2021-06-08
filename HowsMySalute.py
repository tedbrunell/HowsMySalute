#!/usr/bin/env python
# coding: utf-8

# Import Libraries

import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
from matplotlib import pyplot as plt


# Define Functione to calculate the slope/angle between to points


def calculate_angle(a,b):
    a = np.array(a) # First
    b = np.array(b) # Mid
    
    radians = np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = int(np.abs(radians*180.0/np.pi))
    
    if angle >180:
        angle = 360-angle
        
    return angle


# Main
# Variables
upper_arm = ""
forearm = ""
palm = ""
flat = ""
extension = ""

# For webcam input:
cap = cv2.VideoCapture(1)
with mp_holistic.Holistic(model_complexity=1,smooth_landmarks="true",min_detection_confidence=0.6,min_tracking_confidence=0.6) as holistic:

    while cap.isOpened():
        ret, frame = cap.read()

        # Recolor Feed
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False        

        # Make Detections
        image.flags.writeable = False
        joints = holistic.process(image)
        
        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Turn off distracting landmarks
        if joints.pose_landmarks:
            # Facial Landmarks
            joints.pose_landmarks.landmark[0].visibility = 0
            joints.pose_landmarks.landmark[1].visibility = 0
            joints.pose_landmarks.landmark[2].visibility = 0
            joints.pose_landmarks.landmark[3].visibility = 0
            joints.pose_landmarks.landmark[4].visibility = 0
            joints.pose_landmarks.landmark[5].visibility = 0
            joints.pose_landmarks.landmark[6].visibility = 0
            joints.pose_landmarks.landmark[7].visibility = 0
            joints.pose_landmarks.landmark[8].visibility = 0
            joints.pose_landmarks.landmark[9].visibility = 0
            joints.pose_landmarks.landmark[10].visibility = 0
            # Extra hand landmarks
            #joints.pose_landmarks.landmark[17].visibility = 0
            #joints.pose_landmarks.landmark[18].visibility = 0
            #joints.pose_landmarks.landmark[19].visibility = 0
            #joints.pose_landmarks.landmark[20].visibility = 0
            #joints.pose_landmarks.landmark[21].visibility = 0
            #joints.pose_landmarks.landmark[22].visibility = 0

        # Draw face landmarks
        mp_drawing.draw_landmarks(image, joints.face_landmarks, mp_holistic.FACE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(80,110,10), thickness=1, circle_radius=1),
                                  mp_drawing.DrawingSpec(color=(80,256,121), thickness=2, circle_radius=1)
                                 )
        # Pose Detections
        mp_drawing.draw_landmarks(image, joints.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(80,110,10), thickness=2, circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(80,256,121), thickness=2, circle_radius=2)
                                 )
        #Right hand
        #mp_drawing.draw_landmarks(image, joints.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
        #                          mp_drawing.DrawingSpec(color=(80,110,10), thickness=2, circle_radius=2),
        #                          mp_drawing.DrawingSpec(color=(80,256,121), thickness=2, circle_radius=2)
        #                         )
        # Left Hand
        #mp_drawing.draw_landmarks(image, joints.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
        #                          mp_drawing.DrawingSpec(color=(80,110,10), thickness=2, circle_radius=2),
        #                          mp_drawing.DrawingSpec(color=(80,256,121), thickness=2, circle_radius=2)
        #                         )

        # Grab pose landmarks
        score = 0

        try:
            pose = joints.pose_landmarks.landmark
        except:
            pass

        try:
            hand = joints.left_hand_landmarks.landmark
        except:
            pass

    # Test if upper arm is parallel to the ground (+- 5 degrees)
        try:
            shoulder = [pose[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].x,pose[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [pose[mp_holistic.PoseLandmark.LEFT_ELBOW.value].x,pose[mp_holistic.PoseLandmark.LEFT_ELBOW.value].y] 

            angle = calculate_angle(shoulder,elbow)

            if angle >= 175 and angle <= 185:
                upper_arm = "GOOD"
            else:
                upper_arm = "not parallel ({})".format(angle)
        except:
            pass

    # Test if forearm is at 45 degree angle (+- 5 degrees)
        try:
            elbow = [pose[mp_holistic.PoseLandmark.LEFT_ELBOW.value].x,pose[mp_holistic.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [pose[mp_holistic.PoseLandmark.LEFT_WRIST.value].x,pose[mp_holistic.PoseLandmark.LEFT_WRIST.value].y]

            angle = calculate_angle(elbow,wrist)
            forearm_angle = angle

            if angle >= 40 and angle <= 50:
                forearm = "GOOD"
            else:
                forearm = "not 45 ({})".format(angle)
        except:
            pass

    # Test if hand is in line with the forearm (+- 5 degrees)
        try:
            wrist = [pose[mp_holistic.PoseLandmark.LEFT_WRIST.value].x,pose[mp_holistic.PoseLandmark.LEFT_WRIST.value].y]
            pinky = [pose[mp_holistic.PoseLandmark.LEFT_PINKY.value].x,pose[mp_holistic.PoseLandmark.LEFT_PINKY.value].y]

            angle = calculate_angle(wrist,pinky)

            if angle >= (forearm_angle - 5) and angle <= (forearm_angle + 5):
                palm = "GOOD"
            else:
                palm = "not in line ({})".format(angle)
        except:
            pass
    
    # Test for a flat hand (able to see palm)
        try:
            wrist = [pose[mp_holistic.PoseLandmark.LEFT_WRIST.value].x,pose[mp_holistic.PoseLandmark.LEFT_WRIST.value].y]
            pinky = [pose[mp_holistic.PoseLandmark.LEFT_PINKY.value].x,pose[mp_holistic.PoseLandmark.LEFT_PINKY.value].y]

            angle = calculate_angle(wrist,pinky)

            if angle >=40 and angle <= 69:
                flat = "GOOD"
            else:
                flat = "twisted {}".format(angle)

        except:
            pass

    # Test if fingers are straight
    #    try:
    #        pinky = [hand[mp_holistic.HandLandmark.PINKY_MCP].x,hand[mp_holistic.HandLandmark.PINKY_MCP].y] 
    #        pinkyt = [hand[mp_holistic.HandLandmark.PINKY_TIP].x,hand[mp_holistic.HandLandmark.PINKY_TIP].y]

    #        angle1 = calculate_angle(pinky,pinkyt)

    #        thumb = [hand[mp_holistic.HandLandmark.THUMB_MCP].x,hand[mp_holistic.HandLandmark.THUMB_MCP].y] 
    #        thumbt = [hand[mp_holistic.HandLandmark.THUMB_MCP].x,hand[mp_holistic.HandLandmark.RING_FINGER_TIP].y]

    #        angle2 = calculate_angle(thumb,thumbt)

    #        if angle1 >=40 and angle1 <= 50: 
    #            extension = "GOOD"
    #            if angle2 < 40 or angle2 > 50:
    #                extension = "not straight 2:{}".format(angle2)
    #            else:
    #                extension = "not straight 1:{}".format(angle1)

    #    except:
    #        pass
    
        # Scoring box

        cv2.rectangle(image, (0,400), (640, 480), (0, 0, 0), -1)

        # Display Class
        cv2.putText(image, 'HOW IS MY SALUTE?', (5,420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, 'Upper Arm:', (5,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, 'Fore Arm :', (5,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, 'Hand in Line:', (325,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(image, 'Palm Flat:', (325,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
     #   cv2.putText(image, 'Fingers:', (325,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Display Probability
        cv2.putText(image, upper_arm, (110,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, forearm, (110,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, palm, (430,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(image, flat, (430,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
     #   cv2.putText(image, ring, (430,420), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

        # Show the image
        cv2.imshow('MediaPipe Pose', image)

        if cv2.waitKey(10) & 0xFF == ord(' '):
            break
cap.release()
cv2.destroyAllWindows()
