#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2
import numpy as np

# Load camera calibration parameters
with np.load( 'TestCV/B.npz' ) as X :
	mtx, dist, _, _ = [ X[i] for i in ('mtx','dist','rvecs','tvecs') ]

def draw(img, corners, imgpts):
	corner = tuple(corners[0].ravel())
	img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
	img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
	return img

def draw2(img, corners, imgpts):
	imgpts = np.int32(imgpts).reshape(-1,2)
	# draw ground floor in green
	img = cv2.drawContours(img, [imgpts[:4]],-1,(0,255,0),-3)
	# draw pillars in blue color
	for i,j in zip(range(4),range(4,8)):
		img = cv2.line(img, tuple(imgpts[i]), tuple(imgpts[j]),(255),3)
	# draw top layer in red color
	img = cv2.drawContours(img, [imgpts[4:]],-1,(0,0,255),3)
	return img

pattern_size = (9, 6)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((pattern_size[0]*pattern_size[1],3), np.float32)
objp[:,:2] = np.mgrid[0:pattern_size[0],0:pattern_size[1]].T.reshape(-1,2)
axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
axis2 = np.float32([[0,0,0], [0,3,0], [3,3,0], [3,0,0],[0,0,-3],[0,3,-3],[3,3,-3],[3,0,-3] ])

# Initialize the camera
camera = cv2.VideoCapture( 0 )
# Get camera parameters
camera_shape = ( int(camera.get( cv2.CAP_PROP_FRAME_HEIGHT )), int(camera.get( cv2.CAP_PROP_FRAME_WIDTH )), 3 )

# Capture and processing loop
while( True ) :
	# Capture a camera frame
	_, image = camera.read()
	# Convert image from BGR to Grayscale
	grayscale = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
	# Find the chessboard corners on the image
	found, corners = cv2.findChessboardCorners( grayscale, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
	if found :
		# Refine the corner positions
		cv2.cornerSubPix( grayscale, corners, (11, 11), (-1, -1), ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.1 ) )
		# Find the rotation and translation vectors.
		_,rvecs, tvecs, inliers = cv2.solvePnPRansac( objp, corners, mtx, dist )
		# project 3D points to image plane
#		imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, dist)
#		img = draw(img,corners2,imgpts)
		imgpts, jac = cv2.projectPoints( axis2, rvecs, tvecs, mtx, dist )
		image = draw2( image, corners, imgpts )

	# Display the resulting frame
	cv2.imshow( 'Augmented Reality', image )
	# Wait for key pressed
	key = cv2.waitKey( 1 ) & 0xFF
	if  key == 27 : break
# Close the windows
cv2.destroyAllWindows()
