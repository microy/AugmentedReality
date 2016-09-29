#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2
import numpy as np

# Overlayed video
video = cv2.VideoCapture( 'test.avi' )
# Get video parameters
video_shape = ( int(video.get( cv2.CAP_PROP_FRAME_HEIGHT )), int(video.get( cv2.CAP_PROP_FRAME_WIDTH )), 3 )
# Initialize the camera
camera = cv2.VideoCapture( 0 )
# Get camera parameters
camera_shape = ( int(camera.get( cv2.CAP_PROP_FRAME_HEIGHT )), int(camera.get( cv2.CAP_PROP_FRAME_WIDTH )), 3 )
# Initialize temporary images for the overlay
blank = np.zeros( video_shape, np.uint8 )
neg_img = np.zeros( camera_shape, np.uint8 )
cpy_img = np.zeros( camera_shape, np.uint8 )
# Overlay video coordinates
source = np.zeros( (4, 2), dtype = np.float32 )
source[1, 0] = video_shape[1]
source[2, :] = [video_shape[1], video_shape[0]]
source[3, 1] = video_shape[0]
# Destination image coordinates
destination = np.zeros( (4, 2), dtype = np.float32 )
# Capture and processing loop
while( True ) :
    # Capture a camera frame
    _, image = camera.read()
    # Read the overlay video
    ok, overlay = video.read()
    # Check if the video has ended
    if not ok :
        video.set( cv2.CAP_PROP_POS_FRAMES, 0 )
        _, overlay = video.read()
    # Convert image from BGR to Grayscale
    grayscale = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
    # Find the chessboard corners on the image
    found, corners = cv2.findChessboardCorners( grayscale, (5, 4), flags = cv2.CALIB_CB_FAST_CHECK )
    # Draw the video on the chessboard
    if found :
        # Refine the corner positions
        cv2.cornerSubPix( grayscale, corners, (11, 11), (-1, -1), ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.1 ) )
        # Destination image coordinates
        destination[:] = [ corners[0, 0], corners[4, 0], corners[19, 0], corners[15, 0] ]
        # Compute the transformation matrix,
        # i.e., transformation required to overlay the display image from 'src' points to 'dst' points on the image
        tranformation_matrix = cv2.getPerspectiveTransform( source, destination )
        # Initialize the temporary images
        blank.fill( 255 )
        neg_img.fill( 0 )
        cpy_img.fill( 0 )
        # Overlay the video on to the camera image
        neg_img = cv2.warpPerspective( overlay, tranformation_matrix, (neg_img.shape[1], neg_img.shape[0]) )
        cpy_img = cv2.warpPerspective( blank, tranformation_matrix, (cpy_img.shape[1], neg_img.shape[0]) )
        cpy_img = cv2.bitwise_not( cpy_img )
        cpy_img = cv2.bitwise_and( cpy_img, image )
        image = cv2.bitwise_or( cpy_img, neg_img )
    # Display the resulting frame
    cv2.imshow( 'Augmented Reality', image )
    # Wait for key pressed
    key = cv2.waitKey( 1 ) & 0xFF
    if  key == ord( 'q' ) : break
# Close the video file
video.release()
# Close the windows
cv2.destroyAllWindows()
