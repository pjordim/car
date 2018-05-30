import operator, math, numpy as np
"""Auxilar library for colour related functions"""

colourDict = {'red':(171,155,213), 'green':(161,204,194), 'orange':(158,185,236), 'white':(255,255,255)}
colourList = ['RED','GREEN','ORANGE','WHITE']

def getClosestColour(c):
	"""Returns a string with the name of the closest colour from a dictionary previously given and a list with the name of colours"""
	global colourDict, colourList
	deltaR = colourDistance(c,colourDict['red'])
	deltaG = colourDistance(c,colourDict['green'])
	deltaO = colourDistance(c,colourDict['orange'])
	deltaW = colourDistance(c,colourDict['white'])
	deltas = np.array([deltaR,deltaG,deltaO,deltaW])
	minDelta = np.argmin(deltas)
	#print 'min is',minDelta, 'from',deltaR, deltaG, deltaO
	return colourList[minDelta]


def colourDistance(c1,c2):
	"""Returns colour distance as the euclidean distance in any 3D colorspace 
	by using sqrt( (a1-a2)**2+(b1-b2)**2+(c1-c2)**2 )
	where a,b,c are the colour values in the chosen 3D colorspace"""
	s = map(operator.sub,c1,c2)
	m = map(operator.mul,s,s)
	return math.sqrt(sum(m))


def averageColour(frame,x0,y0):
	"""Gets a 4 point average colour from a hotspot where values are too white"""
	try:
		c_lim = 250
		x = x0
		y = y0
		while any (c > c_lim for c in frame[y][x]):
			x = x+1
		rcolor = frame[y][x]
		x = x0
		while any( c > c_lim for c in frame[y][x]):
			x = x-1
		lcolor = frame[y][x]
		x = x0
		while any (c > c_lim for c in frame[y][x]):
			y = y+1
		tcolor = frame[y][x]
		y=y0
		while any (c > c_lim for c in frame[y][x]):
			y = y-1
		bcolor = frame[y][x]
		c4 = [sum (x) for x in zip(rcolor, lcolor ,tcolor ,bcolor)]
		c = [x/4 for x in c4]
		colour = getClosestColour(c)
		if colour is not 'WHITE':
			print colour, ' in x:',x0,'y:',y0#, ' from: ',c,':',rcolor,lcolor,tcolor,bcolor
			return colour
	except IndexError:
		print 'NonSaturated colour not found!'