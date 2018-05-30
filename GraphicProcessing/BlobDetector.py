import cv2
import numpy as np;
"""Defines some auxiliar funcitons related with Blob Detectors
""" 

def setBlobDetector():
	bdparams = cv2.SimpleBlobDetector_Params()
	bdparams.minThreshold = 1;
	#bdparams.maxThreshold = 2400;
	bdparams.filterByArea = False
	#bdparams.minArea = 50
	#bdparams.maxArea = 70
	bdparams.filterByCircularity = True
	bdparams.minCircularity = 0.5
	bdparams.maxCircularity = 1
	bdparams.filterByConvexity = False
	bdparams.minConvexity = 0.001
	bdparams.maxConvexity = 0.999
	bdparams.filterByInertia = False
	bdparams.minInertiaRatio = 0.001
	bdparams.maxInertiaRatio = 0.999
	detector = cv2.SimpleBlobDetector(bdparams)
	return detector

def getBlobCenters (img,detector):
	keypoints = detector.detect(img)
	for k in keypoints:
		print k.pt

def getDrawBlobs (img, detector):
	keypoints = detector.detect(img)
	print len(keypoints)
	img_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 	return img_with_keypoints

def getBlobs (img,detector):
	return detector.detect(img)

def drawBlobs(img, blobs,color = (0,0,255)):
	return cv2.drawKeypoints(img, blobs, np.array([]), color, cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
