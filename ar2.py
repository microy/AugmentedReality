#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2
import numpy as np
from Camera import UsbCamera

# Main application
if __name__ == '__main__' :
    # The camera
    camera = cv2.VideoCapture( 0 )
    while( True ) :
        # Capture frame-by-frame
        _, image = camera.read()
        # Find the chessboard corners on the image
        found, corners = cv2.findChessboardCorners( image, pattern_size )
        # Draw the chessboard corners on the image
        if found :
            cv2.drawChessboardCorners( frame, pattern_size, corners, found )
        #    cv2.rectangle( frame, (int(corners[0,0,0]), int(corners[0,0,1])), (int(corners[53,0,0]), int(corners[53,0,1])), (0,255,0), 3 )
        # Display the resulting frame
        cv2.imshow( 'frame', frame )
        # Wait for key pressed
        key = cv2.waitKey( 1 ) & 0xFF
        if  key == ord( 'q' ) : break
        elif key == ord( ' ' ) and found : calibration_images.append( image )
        elif key == ord ( 'c' ) : CameraCalibration( calibration_images )
    # Close the windows
    cv2.destroyAllWindows()
