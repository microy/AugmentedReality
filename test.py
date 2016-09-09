#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2
import numpy as np

# Calibration pattern size
pattern_size = ( 9, 6 )

# Main application
if __name__ == '__main__' :
    cap = cv2.VideoCapture( 0 )
    while( True ) :
        # Capture frame-by-frame
        _, frame = cap.read()
        # Find the chessboard corners on the image
        found, corners = cv2.findChessboardCorners( frame, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
        # Draw the chessboard corners on the image
        if found :
            cv2.drawChessboardCorners( frame, pattern_size, corners, found )
        #    cv2.rectangle( frame, (int(corners[0,0,0]), int(corners[0,0,1])), (int(corners[53,0,0]), int(corners[53,0,1])), (0,255,0), 3 )
        # Display the resulting frame
        cv2.imshow( 'frame', frame )
        # Exit application with the 'q' key
        if cv2.waitKey( 1 ) & 0xFF == ord( 'q' ) : break
    # Close the windows
    cv2.destroyAllWindows()
