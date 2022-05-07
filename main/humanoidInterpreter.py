from turtle import shape
import numpy as np

def findEdge(XY):
    print("finding edge")
    XY = np.array(XY)
    shape = XY.shape
    Xsort = np.argsort(XY[0])
    X = np.take_along_axis(XY[0],Xsort,axis=0)
    Y = np.take_along_axis(XY[1],Xsort,axis=0)
    print("wooo, thats a doosy")

def interpret(input):
    print("got the data :P")
    edgesFound = []
    for i,_ in enumerate(input['X']):#TODO: why tf is there another layer in the array????
        XY = input['X'][i],input['Y'][i]
        edge = findEdge(XY)
        edgesFound.append(edge)
    return input


#perform edge detection on given data

#then some other stuff, idk