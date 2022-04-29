import enum
from genericpath import exists
from re import T
import time
from PIL import Image,ImageTk
import math
from os import path

from matplotlib.pyplot import axis

import UI
import numpy as np
from copy import copy
from numba import jit

#TODO: fix that nets have infinete recursions of itself
#TODO: add log with warning of when the simulation needs smaller dt and make it so that sim redoes with smaller dt
#TODO: try to use numpy tensorproducts instead

#config
class config():
    bufferCount = 100
    dV = 10**-5

class tensor():
    axi = ''
    arr = []
    shape = ()
    def __init__(self, axi, arrayLike = None, shape = None):
        if shape:
            self.arr = np.zeros(shape)
        elif str(type(arrayLike)) != "<class 'NoneType'>":
            try:
                float(arrayLike)
                self.arr = arrayLike
            except:
                self.arr = np.asarray(arrayLike)
        if len(self.arr.shape) != len(axi):
            raise ValueError
        self.axi = axi
        self.shape = self.arr.shape

def tensorOpperation(T1,T1axi,T2):
    if bool(T1axi):
        opList = [0] * len(T1)
        #axiList = [0] * len(T1)
        multiT2 = True
        if len(T2) == 1:
            multiT2 = False
        for i in range(len(T1)):
            if multiT2:
                j = i
            else:
                j = 0
            opList[i] = tensorOpperation(T1[i],T1axi[1:],T2[j])
        if T1axi[0] == 'x':
            return np.sum(opList)
        if T1axi[0] == 'y':
            return np.asarray(opList)
    else:
        return T1*T2

class circuitSim():
    components = []
    nets = {}
    _newNetsSchedule = {'latestComp' : False}
    def __init__(self):
        self.bufferCount = config.bufferCount

    def addComponent(self, type, pos = (0,0), model = None):
        if model:
            self.components.append(type(pos = pos, model = model))
        else:
            self.components.append(type(pos = pos))
        self._updateAll()#will in this case create new nets for all pins

    def renderCircuit(self):
        UI.renderCircuit(self)

    def _addNet(self,compNr,pinNr):
        newNet = net(self.nets,self.bufferCount)
        self.nets[newNet.id] = newNet
        #self.nets.append()
        #id = self.nets[-1].id
        self.components[compNr].connections[pinNr] = newNet.id

    def mergeNets(self,toMerge,componentsReferences=None):
        newId = min(toMerge)
        newNet = copy(self.nets[newId])
        if componentsReferences:
            for cr in componentsReferences:
                self.components[cr[0]].connections[cr[1]] = newNet.id
        else:
            raise NotImplementedError
        newNet.stateBuffer = (self.nets[toMerge[0]].stateBuffer+self.nets[toMerge[1]].stateBuffer)/2
        self.nets[newNet.id] = newNet
        for n in toMerge:
            if n != newNet.id:
                self.nets.pop(n)
    def renameNet(self,start,target):
        if start != target:
            self.nets[target] = self.nets[start]
            for i in range(len(self.components)):
                for j in range(len(self.components[i].connections)):
                    if self.components[i].connections[j] == start:
                        self.components[i].connections[j] = target
            del self.nets[start]
            self.nets[target].id = target
    def addConnection(self,componentConnections):
        netsToMerge = []
        for cc in componentConnections:
            netId = self.components[cc[0]].connections[cc[1]]
            netsToMerge.append(netId)
        self.mergeNets(netsToMerge, componentConnections)
        keys = list(self.nets.keys())
        for i,k in enumerate(keys):
            self.renameNet(k,i)
    def simulate(self,simTime):
        t = 0
        dt = 1
        numbr = 0
        while t < simTime:
            if numbr % 100 == 0:
                print([e.statePrint() for e in self.nets.values()])
            nT = self.prepNetTensor()#netTensor
            nCV = np.zeros(len(nT[0]))#netCurrentVector
            for c in self.components:
                nTCa = np.array([nT[0][c.connections]])
                axi = 'yxyxyx'
                change = tensorOpperation(c.actionTensor,axi,nTCa)
                for i,old in enumerate(nCV[c.connections]):
                    j = c.connections[i]
                    nCV[j] = np.sum([old,change[i]],axis=0)
            Cs = np.asarray([self.nets[k]._capacitance for k in self.nets.keys()])
            for c in self.components:
                for i,j in enumerate(c.connections):
                    Cs[j] += c.pinCapacitances[i]
            dVdts = nCV/Cs
            dVs = dt*dVdts
            numbr += 1
            if max(abs(dVs)) > config.dV:
                print("max dV exceeded, redoing loop...")
                print(f"dt = {dt}")
                dt /= 2
                continue
            elif max(abs(dVs)) < config.dV/10:
                print("min dV dexceeded, doing larger steps...")
                print(f"dt = {dt}")
                dt *= 2
            for i,dV in enumerate(dVs):
                self.nets[i].updateBufferWithV(dV,dt)
            t += dt
        print("done 👏")
            

    def prepNetTensor(self):
        tensor = np.zeros((1,len(self.nets),1,6,1,self.bufferCount))
        for i,n in enumerate(self.nets.values()):
            transposed = np.transpose(n.stateBuffer)
            tensor[0][i][0][0][0] = np.ones(transposed[0].shape)
            tensor[0][i][0][1][0] = transposed[0]
            tensor[0][i][0][2][0] = np.multiply(transposed[0],transposed[0])
            tensor[0][i][0][3][0] = tensor[0][i][0][0][0]
            tensor[0][i][0][4][0] = transposed[1]
            tensor[0][i][0][5][0] = np.multiply(transposed[1],transposed[0])
        #tensor = np.array([tensor])
        #s = list(tensor.shape)
        #tensor = np.reshape(tensor,s[:2]+[1]+[s[2]]+[1]+[s[3]])
        return tensor
    def _scheduleNewNets(self,mode=None):
        if mode:
            self._newNetsSchedule[mode] = True
    def _updateAll(self):
        if self._newNetsSchedule['latestComp']:
            pinsOcupied = [True if e else False for e in self.components[-1].connections]
            for i in range(self.components[-1].pinCount):
                if not pinsOcupied[i]:
                    self._addNet(len(self.components)-1,i)
            self._newNetsSchedule['latestComp'] = False
        

class component(circuitSim):
    #pinCapacitances = []
    rotation = 0
    pinCount = 0
    scale = (1,1)
    _ogPinPositions = []
    pinPositions = []
    actionTensor = np.array([])
    _compImg = Image.open(path.join(path.dirname(__file__),"componentIcons","defaultIcon.jpg"))
    icon = 0
    pos = (0,0)
    connections = []
    def __init__(self, pos, pinCount, imgN, scale, modelName, pinCapacitances, pinPositions = []):
        self.pos = pos
        self.pinCount = pinCount
        self.scale = scale
        try:
            self._compImg = Image.open(path.join(path.dirname(__file__),"componentIcons",imgN))
        except FileNotFoundError:
            print("Component icon not found...")
        self._ogPinPositions = pinPositions
        if len(pinCapacitances) == self.pinCount:
            self.pinCapacitances = pinCapacitances
        self._updateIcon()
        self._updatePinPos()
        self._initPinNets()
        self._loadModelTensor(modelName)
    def _initPinNets(self):
        self.connections = [None for _ in range(self.pinCount)]
        super()._scheduleNewNets(mode = 'latestComp')
    def _updateIcon(self, scaleMultiplier=1):
        scale = self.scale[0]*scaleMultiplier,self.scale[1]*scaleMultiplier
        icon = self._compImg
        icon = icon.rotate(self.rotation*180/math.pi)
        icon = icon.resize(scale, Image.ANTIALIAS)
        self.icon = ImageTk.PhotoImage(icon)
    def _updatePinPos(self):
        c = math.cos(self.rotation)
        s = math.sin(self.rotation)
        rotM = np.array([[c,s],[-s,c]])
        self.pinPositions = self._ogPinPositions
        for i,pp in enumerate(self.pinPositions):
            pp = tuple(np.matmul(rotM,np.asarray(pp)))
            self.pinPositions[i] = pp
    def rotateBy(self,rot):
        rot *= math.pi/180
        self.rotation -= rot
        self._updatePinPos()
        self._updateIcon()
    def _loadModelTensor(self,name):
        self.actionTensor = np.load(path.join(path.dirname(__file__),'componentModels',f'{name}.npy'))
        #self.actionTensor = tensorConstr('yxxx',self.actionTensor)
        s = list(self.actionTensor.shape)
        self.actionTensor = np.reshape(self.actionTensor,s[:2]+[1]+[s[2]]+[1]+[s[3]])

class net(circuitSim):
    _capacitance = 10**-12
    stateBuffer = []
    id = 0
    def __init__(self,existingNets,bufferCount):
        takenIds = []
        for n in existingNets.keys():
            takenIds.append(existingNets[n].id)
        takenIds.sort()
        for id in range(len(takenIds)):
            if takenIds[id] != id:
                self.id = id
                return
        self.id = len(takenIds)
        self.stateBuffer = np.zeros((bufferCount,2))

    def updateBufferWithV(self,dV,dt):
        V = self.stateBuffer[0][0] + dV
        dVdt = dV/dt
        nS = np.array([V,dVdt])
        self.stateBuffer = np.insert(self.stateBuffer,0,nS,axis=0)[:-1]

    def cleanBuffer(self):
        for i in range(len(self.stateBuffer),self.bufferCount,-1):
            self.stateBuffer[i].pop(i)

    def statePrint(self):
        vals = copy(self.stateBuffer[0])
        vals = ['{:.10f}'.format(round(v,10)) for v in vals]
        vals[0] = f'{vals[0]}V'
        vals[1] = f'{vals[1]}V/s'
        return vals

class opamp(component,circuitSim):
    def __init__(self, scale=(10,10), pos=(50,50), model = None):
        super().__init__(
            pos, 
            5,
            "opAmpIcon.png", 
            scale,
            model,
            pinCapacitances=[],
            pinPositions = [(0.45,0),(-0.01,0.315),(0,-0.33),(-0.5,0.25),(-0.5,-0.25)]
            )

class resistor(component,circuitSim):
    def __init__(self, scale=(3,3), pos=(0,0), model = 'res1k'):
        super().__init__(
            pos, 
            2,
            "resistor.png", 
            scale,
            model,
            pinCapacitances=[0,0],
            pinPositions = [(-0.5,0),(0.5,0)]
            )

class supply(component,circuitSim):
    _maxCurrent = 0
    def __init__(self, scale=(2,2), pos=(0,0), model = "supply0v"):#make a more advanced with constant current input by a square wave
        super().__init__(
            pos, 
            1,
            "supply.png", 
            scale,
            model,
            pinCapacitances=[10*(10**(-6))],
            pinPositions = [(0.5,0)]
            )

class caps(component):
    capacitance = 1
    def __init__(self, scale=(3,3), pos=(0,0), model = 'cap'):
        super().__init__(
            pos, 
            2,
            "cCap.png", 
            scale,
            model,
            pinCapacitances=[100*(10**(-6)),100*(10**(-6))],
            pinPositions = [(-0.5,0),(0.5,0)]
            )

class eCap(caps):
    def __init__(self, pos=(0,0), model = None):
        super().__init__(pos = pos, model = model)

class cCap(caps):
    def __init__(self, pos=(0,0), model = None):
        super().__init__(pos = pos, model = model)

def main():
    c = circuitSim()
    c.addComponent(supply, pos = (15,5), model='supply9V')
    c.components[-1].rotateBy(90)
    c.addComponent(resistor, pos = (15,10), model='res1k')
    c.components[-1].rotateBy(90)
    #c.components[-1].resistance = 1000
    #c.addComponent(cCap, pos = (15,20), model='cap')
    #c.components[2].rotateBy(90)
    #c.components[2].capacitance = 10**(-5)
    c.addComponent(supply, pos = (15,25), model='supply0V')
    c.components[-1].rotateBy(-90)
    c.addConnection([[0,0],[1,0]])
    c.addConnection([[1,1],[2,0]])
    #c.addConnection([[2,1],[3,0]])
    #c.renderCircuit()
    c.simulate(0.01)

if __name__ == '__main__':
    main()        