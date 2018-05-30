from CinematicaInversa import CinematicaInversa
import numpy as np


IC = CinematicaInversa(100,np.deg2rad(20),0.09,0.125,0.07,10,0.043)
print '-----',0,0.25, '::',[IC.LinearSpeedToDutyCycle(e) for e in IC.getLinearSpeed(0,0.25)],'-----'
print
print '-----',-50,0.25, '::',[IC.LinearSpeedToDutyCycle(e) for e in IC.getLinearSpeed(-50,0.25)],'-----'
print
print '-----',-100,0.25, '::',[IC.LinearSpeedToDutyCycle(e) for e in IC.getLinearSpeed(-100,0.25)],'-----'
print
print '-----',50,0.25, '::',[IC.LinearSpeedToDutyCycle(e) for e in IC.getLinearSpeed(50,0.25)],'-----'
print
print '-----',100,0.25, '::',[IC.LinearSpeedToDutyCycle(e) for e in IC.getLinearSpeed(100,0.25)],'-----'
