#!/usr/bin/env python
# coding: utf-8

# Import Libraries

import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
from matplotlib import pyplot as plt

class salute(object):
    # Define Functione to calculate the slope/angle between to points
    def calculate_angle(self,a,b):
        a = np.array(a) # First
        b = np.array(b) # Mid
    
        radians = np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = int(np.abs(radians*180.0/np.pi))
    
        if angle >180:
            angle = 360-angle
        
        return angle

    def __init__(self):
        # For webcam input:
        self.cap = cv2.VideoCapture(-1, cv2.CAP_V4L) 

    def get_salute(self):   
        with mp_pose.Pose(model_complexity=1,smooth_landmarks="true",min_detection_confidence=0.6,min_tracking_confidence=0.6) as pose:
            ret, frame = self.cap.read()

            while self.cap.isOpened():
            
                # Recolor Feed and flip the image
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Make Detections
                image.flags.writeable = False
                joints = pose.process(image)

                # Draw the pose annotation on the image.
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                
                # Turn off distracting landmarks
                
                if joints.pose_landmarks:
                
                    # Facial Landmarks
                    # joints.pose_landmarks.landmark[0].visibility = 0
                    joints.pose_landmarks.landmark[1].visibility = 0
                    # joints.pose_landmarks.landmark[2].visibility = 0
                    joints.pose_landmarks.landmark[3].visibility = 0
                    joints.pose_landmarks.landmark[4].visibility = 0
                    # joints.pose_landmarks.landmark[5].visibility = 0
                    joints.pose_landmarks.landmark[6].visibility = 0
                    # joints.pose_landmarks.landmark[7].visibility = 0
                    # joints.pose_landmarks.landmark[8].visibility = 0
                    # joints.pose_landmarks.landmark[9].visibility = 0
                    # joints.pose_landmarks.landmark[10].visibility = 0

                # Draw Pose Detections

                mp_drawing.draw_landmarks(image, joints.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(80,110,10), thickness=2, circle_radius=2),
                                          mp_drawing.DrawingSpec(color=(80,256,121), thickness=2, circle_radius=2)
                                          )

                # Grab pose landmarks and calculate slope

                # Test if upper arm is parallel to the ground
                try:
                    pose = joints.pose_landmarks.landmark
                except:
                    pass

                # Test if upper arm is parallel to the ground (+- 5 degrees)
                try:
                    pt1 = [pose[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,pose[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                    pt2 = [pose[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,pose[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]

                    angle = self.calculate_angle(pt1,pt2)

                    if angle <= 5:
                        uparm = "GOOD"
                    else:
                        uparm = "not parallel"
                except:
                    uparm = ""
                    pass

                # Test if forearm is at 45 degree angle (+- 5 degrees)
                try:
                    pt1 = [pose[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,pose[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
                    pt2 = [pose[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,pose[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

                    angle = self.calculate_angle(pt1,pt2)
                    forearm_angle = angle

                    if angle >= 130 and angle <= 140:
                        forearm = "GOOD"
                    else:
                        forearm = "not at 45"
                except:
                    forearm = ""
                    pass

                # Test if hand is in line with the forearm (+-8  degrees)
                try:
                    pt1 = [pose[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,pose[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    pt2 = [pose[mp_pose.PoseLandmark.RIGHT_PINKY.value].x,pose[mp_pose.PoseLandmark.RIGHT_PINKY.value].y]

                    angle = self.calculate_angle(pt1,pt2)

                    if angle >= (forearm_angle - 8) and angle <= (forearm_angle + 8):
                        palm = "GOOD"
                    else:
                        palm = "not in line"
                except:
                    palm = ""
                    pass

                # Test for a flat hand (able to see palm)
                try:
                    pt1 = [pose[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,pose[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
                    pt2 = [pose[mp_pose.PoseLandmark.RIGHT_PINKY.value].x,pose[mp_pose.PoseLandmark.RIGHT_PINKY.value].y]

                    angle = self.calculate_angle(pt1,pt2)

                    if angle >=130 and angle <= 140:
                        flat = "GOOD"
                    else:
                        flat = "not visible"

                except:
                    flat = ""
                    pass


                #Flip the image
                image = cv2.flip(image, 1)
                
                # Scoring box
                cv2.rectangle(image, (0,400), (640, 480), (45, 45, 45), -1)

                # Display Part
                cv2.putText(image, 'HOW IS YOUR SALUTE?', (5,420), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, 'Upper Arm:', (5,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, 'Fore Arm :', (5,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, 'Hand in Line:', (325,440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, 'Palm Flat:', (325,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                # cv2.putText(image, 'Fingers:', (325,460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                # Display Score
                cv2.putText(image, uparm, (110,440), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, forearm, (110,460), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, palm, (435,440), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(image, flat, (435,460), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                # cv2.putText(image, fingers, (430,420), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                ret, jpeg = cv2.imencode(".jpg", image)
                return jpeg.tobytes()

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
