import os
import sys

class asset():
    def __init__(self,ID:int):
        self.pos = (0,0)
        self.size = (1,1)
        self.clickOpp = {}
        self.toggleVars = {}
        self.pos_toggles = []
        self.size_toggles = []
        self.clickOpp_toggles = []
        self.toggleAble = False
        self.instanceId = ID
        self.instaceId = 0

    def updateAfterToggle(self):
        self.pos = self.toggleVars['pos'][0]
        self.size = self.toggleVars['size'][0]
        self.clickOpp = self.toggleVars['clickOpp'][0]

    def toggle(self,toggleTo:int):
        for k in self.toggleVars.keys():
            self.toggleVars[k][1].insert(toggleTo,self.toggleVars[k][0])
            self.toggleVars[k][0] = self.toggleVars[k][1][toggleTo+1]
            self.toggleVars[k][1].pop(toggleTo+1)
        self.updateAfterToggle()

    def initTogglevars(self):
        self.toggleVars['pos'] = [self.pos,self.pos_toggles]
        self.toggleVars['size'] = [self.size,self.size_toggles]
        self.toggleVars['clickOpp'] = [self.clickOpp,self.clickOpp_toggles]

class sprite(asset):
    type = 'sprite'
    def __init__(self, ID:int, pos = None, img = 'defaultIcon.jpg', size = None, clickOpp = None, toggleAble = False):
        super().__init__(ID)
        self.imgPath = None    
        self.imgPath_togggles = []
        if pos != None:
            self.pos = pos
        if size != None:
            self.size = size
        if img in os.listdir(os.path.join(sys.path[0],'UIAssets')):
            self.imgPath = os.path.join(sys.path[0],'UIAssets',img)
        else:
            self.imgPath = os.path.join(sys.path[0],'UIAssets','defaultIcon.jpg')
        self.toggleVars['imgPath'] = ([self.imgPath,self.imgPath_togggles])
        if clickOpp != None:
            self.clickOpp = clickOpp
        super().initTogglevars()

    def updateAfterToggle(self):
        super().updateAfterToggle()
        self.imgPath = self.toggleVars['imgPath'][0]

    def toggle(self,toggleTo:int):
        super().toggle(toggleTo)
        self.updateAfterToggle()

class button(asset):
    type = 'button'
    def __init__(self, ID:int, allignment = None, text = None, command = None, cmdArgs = None):
        super().__init__(ID)
        self.allignment = ''
        self.text = ''
        self.command = None
        self.cmdArgs = {}
        self.allignment_toggles = []
        self.text_toggles = []
        self.command_toggles = []
        self.cmdArgs_toggles = []
        if allignment != None:
            self.allignment = allignment
        if text != None:
            self.text = text
        if command != None:
            self.command = command
        if cmdArgs != None:
            self.cmdArgs = cmdArgs
        self.toggleVars['allignment'] = [self.allignment,self.allignment_toggles]
        self.toggleVars['text'] = [self.text,self.text_toggles]
        self.toggleVars['command'] = [self.command,self.command_toggles]
        self.toggleVars['cmdArgs'] = [self.cmdArgs,self.cmdArgs_toggles]
        super().initTogglevars()

    def updateAfterToggle(self):
        super().updateAfterToggle()
        self.allignment = self.toggleVars['allignment'][0]
        self.text = self.toggleVars['text'][0]
        self.command = self.toggleVars['command'][0]
        self.cmdArgs = self.toggleVars['cmdArgs'][0]
    
    def toggle(self,toggleTo:int):
        super().toggle(toggleTo)
        self.updateAfterToggle()

class entry(asset):
    type = 'entry'
    def __init__(self, ID:int, text = None, targetVar = None, row = 0, column = 0,expectedDataType = 'String'):
        super().__init__(ID)
        self.text = ''
        if text != None:
            self.text = text
        if targetVar != None:
            self.targetVar = targetVar
        self.row = row
        self.column = column
        self.expectedDataType = expectedDataType
        super().initTogglevars()

class scene():
    assets = []
    windowSettings = 0
    returnVars = {}
    def __init__(self):
        pass