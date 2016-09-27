#! /usr/bin/env python
# -*- coding:utf-8 -*-

#
# Augmented reality demonstration application
#

# External dependencies
import sys
import cv2
import numpy as np
from PyQt4 import QtCore
from PyQt4 import QtGui
from Camera import UsbCamera


# User interface
class Widget( QtGui.QWidget ) :
	# Signal sent to update the image in the widget
	update_image = QtCore.pyqtSignal()
	# Initialization
	def __init__( self, parent = None ) :
		# Initialise QWidget
		super( Widget, self ).__init__( parent )
		# Set the window title
		self.setWindowTitle( 'Camera Calibration' )
		# Connect the signal to update the image
		self.update_image.connect( self.UpdateImage )
		# Widget to display the images from the cameras
		self.image_widget = QtGui.QLabel( self )
		self.image_widget.setScaledContents( True )
		# Widget element
		self.button_activate_ar = QtGui.QPushButton( 'Activate AR', self )
		self.button_activate_ar.setCheckable( True )
		self.button_activate_ar.setShortcut( 'F1' )
		self.button_activate_ar.clicked.connect( self.ToggleAR )
		self.ar_activated = False
		# Widget layout
		self.layout_global = QtGui.QVBoxLayout( self )
		self.layout_global.addWidget( self.image_widget )
		self.layout_global.addWidget( self.button_activate_ar )
		self.layout_global.setSizeConstraint( QtGui.QLayout.SetFixedSize )
		# Set the Escape key to close the application
		QtGui.QShortcut( QtGui.QKeySequence( QtCore.Qt.Key_Escape ), self ).activated.connect( self.close )
		# Chessboard pattern size
		self.pattern_size = ( 5, 4 )
		# Initialize the USB camera
		self.camera = UsbCamera()
		# Initialize the video
#		self.video = cv2.VideoCapture( 'test.avi' )
		self.video = cv2.imread( 'shingani.jpg' )
		# Fix the widget size
		self.image_widget.setFixedSize( self.camera.width, self.camera.height )
		# Start image acquisition
		self.camera.StartCapture(  self.ImageCallback  )
	def ToggleAR( self ) :
		self.ar_activated = not self.ar_activated
	# Receive the frame sent by the camera
	def ImageCallback( self, image ) :
		# Get the image
		self.image = image
		# Process the images
		self.update_image.emit()
	# Process the given image for display
	def UpdateImage( self ) :
		# Copy image for display
		image = np.copy( self.image )
		# Process the image if the AR is activated
		if self.ar_activated :
			# Convert image from BGR to Grayscale
			grayscale_image = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
			# Find the chessboard corners on the image
			found, corners = cv2.findChessboardCorners( grayscale_image, self.pattern_size, flags = cv2.CALIB_CB_FAST_CHECK )
			# Draw the video on the chessboard
			if found :
				# Refine the corner positions
				cv2.cornerSubPix( grayscale_image, corners, (11, 11), (-1, -1), ( cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 30, 0.1 ) )
				# Overlay image coordinates
				source = []
				source.append( [0, 0] )
				source.append( [self.video.shape[1], 0] )
				source.append( [self.video.shape[1], self.video.shape[0]] )
				source.append( [0, self.video.shape[0]] )
				source = np.array( source, dtype = np.float32 )
				# Destination image coordinates
				destination = []
				destination.append( corners[0].flatten() )
				destination.append( corners[4].flatten() )
				destination.append( corners[19].flatten() )
				destination.append( corners[15].flatten() )
				destination = np.array( destination, dtype = np.float32 )
				# Compute the transformation matrix,
				# i.e., transformation required to overlay the display image from 'src' points to 'dst' points on the image
				tranformation_matrix = cv2.getPerspectiveTransform( source, destination )
				blank = np.zeros( self.video.shape, self.video.dtype )
				neg_img = np.zeros( image.shape, image.dtype )
				cpy_img = np.zeros( image.shape, image.dtype )
				blank = cv2.bitwise_not( blank )
				neg_img = cv2.warpPerspective( self.video, tranformation_matrix, (neg_img.shape[1], neg_img.shape[0]) )
				cpy_img = cv2.warpPerspective( blank, tranformation_matrix, (cpy_img.shape[1], neg_img.shape[0]) )
				cpy_img = cv2.bitwise_not( cpy_img )
				cpy_img = cv2.bitwise_and( cpy_img, image )
				image = cv2.bitwise_or( cpy_img, neg_img )

		# Convert image color format from BGR to RGB
		image = cv2.cvtColor( image, cv2.COLOR_BGR2RGB )
		# Create a Qt image
		qimage = QtGui.QImage( image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888 )
		# Set the image to the Qt widget
		self.image_widget.setPixmap( QtGui.QPixmap.fromImage( qimage ) )
		# Update the widget
		self.image_widget.update()
	# Close the widgets
	def closeEvent( self, event ) :
		# Stop image acquisition
		self.camera.StopCapture()
		# Stop the video
#		self.video.release()
		# Close main application
		event.accept()


# Main application
if __name__ == '__main__' :
	application = QtGui.QApplication( sys.argv )
	widget = Widget()
	widget.show()
	sys.exit( application.exec_() )
