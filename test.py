#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import cv2
import numpy as np
import threading
from PyQt4 import QtCore
from PyQt4 import QtGui


# Calibration pattern size
pattern_size = ( 9, 6 )




# Stereovision user interface
class CalibrationWidget( QtGui.QWidget ) :
	# Signal sent to update the image in the widget
	update_image = QtCore.pyqtSignal( np.ndarray )
	# Initialization
	def __init__( self, parent = None ) :
		# Initialise QWidget
		super( CalibrationWidget, self ).__init__( parent )
		# Set the window title
		self.setWindowTitle( 'Camera Calibration' )
		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )
		# Widget to display the images from the cameras
		self.image_widget = QtGui.QLabel( self )
		self.image_widget.setScaledContents( True )
		# Widget elements
		self.button_chessboard = QtGui.QPushButton( 'Chessboard', self )
		self.button_chessboard.setCheckable( True )
		self.button_chessboard.setShortcut( 'F1' )
		self.button_chessboard.clicked.connect( self.ToggleChessboard )
		self.button_calibration = QtGui.QPushButton( 'Calibration', self )
		self.button_calibration.setShortcut( 'F2' )
		self.spinbox_pattern_rows = QtGui.QSpinBox( self )
		self.spinbox_pattern_rows.setValue( pattern_size[0] )
		self.spinbox_pattern_rows.valueChanged.connect( self.UpdatePatternSize )
		self.spinbox_pattern_cols = QtGui.QSpinBox( self )
		self.spinbox_pattern_cols.setValue( pattern_size[1] )
		self.spinbox_pattern_cols.valueChanged.connect( self.UpdatePatternSize )
		# Widget layout
		self.layout_pattern_size = QtGui.QHBoxLayout()
		self.layout_pattern_size.addWidget( QtGui.QLabel( 'Calibration pattern size :' ) )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_rows )
		self.layout_pattern_size.addWidget( self.spinbox_pattern_cols )
		self.layout_controls = QtGui.QHBoxLayout()
		self.layout_controls.addWidget( self.button_chessboard )
		self.layout_controls.addWidget( self.button_calibration )
		self.layout_controls.addLayout( self.layout_pattern_size )
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.image_widget )
		self.layout_global.addLayout( self.layout_controls )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		# Initialize the USB stereo cameras
		self.camera = UsbCamera()
		# Lower the camera frame rate and resolution
		self.camera.camera.set( cv2.CAP_PROP_FRAME_WIDTH, 640 )
		self.camera.camera.set( cv2.CAP_PROP_FRAME_HEIGHT, 480 )
		self.camera.camera.set( cv2.CAP_PROP_FPS, 5 )
		# Fix the widget size
		self.image_widget.setFixedSize( self.camera.width, self.camera.height )
		# Start image acquisition
		self.stereo_camera.StartCapture(  self.ImageCallback  )
	# Receive the frame sent by the camera
	def ImageCallback( self, image ) :
		# Process the images
		self.update_image.emit( image )
	# Process the given stereo images
	def UpdateImage( self, image ) :
		# Get the image
		self.image = image
		# Copy images for display
		image_displayed = np.copy( self.image )
		# Preview the calibration chessboard on the image
		if self.chessboard_enabled :
			image_displayed = PreviewChessboard( image_displayed )
		# Create a Qt image
		qimage = QtGui.QImage( image_displayed, image_displayed.shape[1], image_displayed.shape[0], QtGui.QImage.Format_RGB888 )
		# Set the image to the Qt widget
		self.image_widget.setPixmap( QtGui.QPixmap.fromImage( qimage ) )
		# Update the widget
		self.image_widget.update()
	# Toggle the chessboard preview
	def ToggleChessboard( self ) :
		self.chessboard_enabled = not self.chessboard_enabled
	# Stereo camera calibration
	def Calibration( self ) :
		self.calibration = CameraCalibration()
	# Update the calibration pattern size
	def UpdatePatternSize( self, _ ) :
		pattern_size = ( self.spinbox_pattern_rows.value(), self.spinbox_pattern_cols.value() )
	# Close the widgets
	def closeEvent( self, event ) :
		# Stop image acquisition
		self.camera.StopCapture()
		# Close main application
		event.accept()





# Thread to read the images from a USB camera
class UsbCamera( threading.Thread ) :
	# Initialisation
	def __init__( self ) :
		# Initialize the thread
		super( UsbCamera, self ).__init__()
		# Initialize the cameras
		self.camera = cv2.VideoCapture( 0 )
	# Return the image width
	@property
	def width( self ) :
		return self.camera.get( cv2.CAP_PROP_FRAME_WIDTH )
	# Return the image height
	@property
	def height( self ) :
		return self.camera.get( cv2.CAP_PROP_FRAME_HEIGHT )
	# Start acquisition
	def StartCapture( self, image_callback ) :
		# Function called when the images are received
		self.image_callback = image_callback
		# Start the capture loop
		self.running = True
		self.start()
	# Stop acquisition
	def StopCapture( self ) :
		self.running = False
		self.join()
	# Thread main loop
	def run( self ) :
		# Thread running
		while self.running :
			# Capture images
			self.camera.grab()
			# Get the images
			_, image = self.camera.retrieve()
			# Send the image via the external callback function
			self.image_callback( image )
		# Release the cameras
		self.camera.release()



# Save the calibration parameters to a file
def SaveCalibration( calibration, filename = 'calibration.pkl' ) :
	# Write the calibration object with all the parameters
	with open( filename, 'wb') as calibration_file :
		pickle.dump( calibration, calibration_file, pickle.HIGHEST_PROTOCOL )

# Find the chessboard quickly, and draw it
def PreviewChessboard( image ) :
	# Find the chessboard corners on the image
	found, corners = cv2.findChessboardCorners( image, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
#	found, corners = cv2.findCirclesGridDefault( image, pattern_size, flags = cv2.CALIB_CB_ASYMMETRIC_GRID )
	# Draw the chessboard corners on the image
	if found : cv2.drawChessboardCorners( image, pattern_size, corners, found )
	# Return the image with the chessboard if found
	return image


# Camera calibration
def CameraCalibration( image_files ) :
	# Chessboard pattern
	pattern_points = np.zeros( (np.prod(pattern_size), 3), np.float32 )
	pattern_points[:,:2] = np.indices(pattern_size).T.reshape(-1, 2)
	# Asymetric circles grid pattern
#	pattern_points = []
#	for i in xrange( pattern_size[1] ) :
#		for j in xrange( pattern_size[0] ) :
#			pattern_points.append( [ (2*j) + i%2 , i, 0 ] )
#	pattern_points = np.asarray( pattern_points, dtype=np.float32 )
	# Get image size
	height, width = image_files[0].shape[:2]
#	img_size = tuple( cv2.pyrDown( cv2.imread( image_files[0] ), cv2.CV_LOAD_IMAGE_GRAYSCALE ).shape[:2] )
	img_size = ( width, height )
	# 3D points
	obj_points = []
	# 2D points
	img_points = []
	# Images with chessboard found
	img_files = []
	# For each image
	for filename in image_files :
		# Load the image
		image = cv2.imread( filename, cv2.IMREAD_GRAYSCALE )
		# Resize image
	#	image_small = cv2.resize( image, None, fx=image_scale, fy=image_scale )
	#	image_small = cv2.pyrDown( image )
	#	image = image_small
		image_small = image
		# Chessboard detection flags
		flags  = 0
		flags |= cv2.CALIB_CB_ADAPTIVE_THRESH
		flags |= cv2.CALIB_CB_NORMALIZE_IMAGE
		# Find the chessboard corners on the image
		found, corners = cv2.findChessboardCorners( image_small, pattern_size, flags=flags )
	#	found, corners = cv2.findCirclesGridDefault( image, pattern_size, flags = cv2.CALIB_CB_ASYMMETRIC_GRID )
		# Pattern not found
		if not found :
			print( 'Pattern not found on image {}...'.format( filename ) )
			continue
		# Rescale the corner position
	#	corners *= 1.0 / image_scale
	#	corners *= 2.0
		# Termination criteria
		criteria = ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 1e-5 )
		# Refine the corner positions
		cv2.cornerSubPix( image, corners, (11, 11), (-1, -1), criteria )
		# Store image and corner informations
		img_points.append( corners.reshape(-1, 2) )
		obj_points.append( pattern_points )
		img_files.append( filename )
	# Camera calibration flags
	flags  = 0
#	flags |= cv2.CALIB_USE_INTRINSIC_GUESS
#	flags |= cv2.CALIB_FIX_PRINCIPAL_POINT
#	flags |= cv2.CALIB_FIX_ASPECT_RATIO
#	flags |= cv2.CALIB_ZERO_TANGENT_DIST
	flags |= cv2.CALIB_RATIONAL_MODEL
#	flags |= cv2.CALIB_FIX_K3
	flags |= cv2.CALIB_FIX_K4
	flags |= cv2.CALIB_FIX_K5
	# Camera calibration
	calibration = cv2.calibrateCamera( obj_points, img_points, img_size, None, None, flags=flags )
	# Store the calibration results in a dictionary
	parameter_names = ( 'calib_error', 'camera_matrix', 'dist_coefs', 'rvecs', 'tvecs' )
	calibration = dict( zip( parameter_names, calibration ) )
	# Compute reprojection error
	calibration['reproject_error'] = 0
	for i, obj in enumerate( obj_points ) :
		# Reproject the object points using the camera parameters
		reprojected_img_points, _ = cv2.projectPoints( obj, calibration['rvecs'][i],
		calibration['tvecs'][i], calibration['camera_matrix'], calibration['dist_coefs'] )
		# Compute the error with the original image points
		error = cv2.norm( img_points[i], reprojected_img_points.reshape(-1, 2), cv2.NORM_L2 )
		# Add to the total error
		calibration['reproject_error'] += error * error
	calibration['reproject_error'] = math.sqrt( calibration['reproject_error'] / (len(obj_points) * np.prod(pattern_size)) )
	# Backup calibration parameters for future use
	calibration['img_points'] = img_points
	calibration['obj_points'] = obj_points
	calibration['img_size'] = img_size
	calibration['img_files'] = img_files
	calibration['pattern_size'] = pattern_size
	# Return the camera calibration results
	return calibration


# Main application
if __name__ == '__main__' :
    # Calibration images
    calibration_images = []
    cap = cv2.VideoCapture( 0 )
    while( True ) :
        # Capture frame-by-frame
        _, frame = cap.read()
        # Find the chessboard corners on the image
        found, corners = cv2.findChessboardCorners( frame, pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
        image = np.copy( frame )
        # Draw the chessboard corners on the image
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
