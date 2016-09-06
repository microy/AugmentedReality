#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2

# Main application
if __name__ == '__main__' :
    cap = cv2.VideoCapture( 0 )
    while( True ) :
        # Capture frame-by-frame
        _, frame = cap.read()
        # Display the resulting frame
        cv2.imshow( 'frame', frame )
        if cv2.waitKey( 1 ) & 0xFF == ord( 'q' ) : break
    # When everything done, release the capture
    cap.release()
#    cv2.destroyAllWindows()
