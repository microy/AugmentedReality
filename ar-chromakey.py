#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2
import numpy as np

# Collect video input from first webcam on system
video_capture = cv2.VideoCapture(0)
# Live camera feed
while True :
    # Capture video feed
    _, frame = video_capture.read()
    #
    frame2 = np.where( frame < 150, frame, 0 )
    # Display the resulting frame
    cv2.imshow( 'Video', frame )
    cv2.imshow( 'Process', frame2 )
    # Press Escape key to exit
    if cv2.waitKey(1) & 0xFF == 27 : break
# When everything is done, release the capture
cv2.destroyAllWindows()
