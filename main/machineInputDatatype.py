from dataclasses import dataclass
import numpy as np

def addTime2Point(point, time):
    return np.append(point, time)

@dataclass
class _coordinatePoint():
    def __init__(self, coordinate : np.array, point : np.array):
        self.inoutRatio = len(point) / len(coordinate)
        self.coordinate = coordinate
        self.point = point


@dataclass
class machineInput():
    """
    This class is the datatype that is used to store the input data in a mathematical interpretation.
    """
    #stores a numerical mapping across the full vectorspace
    coordinates = np.array([])
    truthTable = np.array([])

    def __init__(self,inPinCount : int, outPinCount : int, proporgationDelay : int = 0):
        self.proporgationDelay = proporgationDelay
        self.inPinCount = inPinCount
        self.outPinCount = outPinCount
    
    def addCoordinate(self, coordinate : np.array, point : np.array):
        if len(self.coordinates) == 0:
            if len(point)/len(coordinate) != self.coordinates[0].inoutRatio:
                raise ValueError("The input point does not have the same inoutRatio as previous ones.")
        self.coordinates.append(_coordinatePoint(coordinate, point))
    
    def addTruthTablePoint(self, inPins : np.array, outPins : np.array, propergationDelay : int = None):
        if propergationDelay is None:
            propergationDelay = self.proporgationDelay
        if len(self.truthTable) == 0:
            if len(outPins) != self.outPinCount:
                raise ValueError("The output point does not have the same length as the output pin count.")
            if len(inPins) != self.inPinCount:
                raise ValueError("The input point does not have the same length as the input pin count.")
        inPoint = addTime2Point(inPins, 0)
        outPoint = addTime2Point(outPins, propergationDelay)
        self.truthTable.append(_coordinatePoint(inPins, outPins))
    

