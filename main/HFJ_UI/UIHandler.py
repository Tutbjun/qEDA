import tkinter as tk
import tkinter.font as font
from PIL import Image,ImageTk
from copy import copy
import numpy as np
import os
from functools import partial
from configImporter.configImport import getConfig
configs = getConfig(__file__)


_defaults = {}
def init(config):
    for k in configs['UIHandler']['SETTINGS'].keys():
        _defaults[k.lower()] = configs['UIHandler']['SETTINGS'][k]
    pass

class UIReturnData():
    succes = False
    returnVar = {}

class _entryVar(tk.StringVar):
    expectedType = None
    def __init__(self,expectedType = None):
        super().__init__()
        self.expectedType = expectedType

class UIInstance:
    def _makeCanvas(self,tkWindow : tk.Tk, windowSettings : dict):
        if 'FULLSCREEN' in windowSettings:
            tkWindow.attributes('-fullscreen', windowSettings['FULLSCREEN'])
        else:
            tkWindow.attributes('-fullscreen', _defaults['fullscreen'])
        w,h = 0,0
        ratio = 0
        if 'RATIO' in windowSettings:
            ratio = windowSettings['RATIO'][0]/windowSettings['RATIO'][1]
        else:
            ratio = _defaults['ratio'][0]/_defaults['ratio'][1]
        if 'RESOLUTION' in windowSettings:
            h = windowSettings['RESOLUTION']
        else:
            h = _defaults['resolution']
        w = int(h*ratio)
        canvas = tk.Canvas(tkWindow, width=w, height=h)   
        canvas.pack()
        return tkWindow, canvas

    def _posConverter(self,tkWindow : tk.Tk, windowSettings : dict, pos):
        newPos = np.array([0,0])
        windowPxSize = [tkWindow.winfo_screenwidth(),tkWindow.winfo_screenheight()]
        if _defaults['coordinate_origin'] == 'center':
            newPos = [windowPxSize[0]/2,windowPxSize[1]/2]
        else:
            raise NotImplementedError
        if _defaults['coordinatemode'] == 'cm':
            posShift = np.array(copy(pos),dtype=float)
            posShift[0] /= windowSettings['SIZE_REALWORLD'][0]
            posShift[1] /= windowSettings['SIZE_REALWORLD'][1]
            posShift[0] *= windowPxSize[0]
            posShift[1] *= windowPxSize[1]
            newPos += posShift
        else:
            raise NotImplementedError
        newPos = list(newPos)
        return newPos[0],newPos[1]

    def _sizeConverter(self,tkWindow : tk.Tk, windowSettings : dict, size):
        newSize = [1,1]
        windowPxSize = [tkWindow.winfo_screenwidth(),tkWindow.winfo_screenheight()]
        if _defaults['coordinatemode'] == 'cm':
            newSize = copy(size)
            newSize[0] /= windowSettings['SIZE_REALWORLD'][0]
            newSize[1] /= windowSettings['SIZE_REALWORLD'][1]
            newSize[0] *= windowPxSize[0]
            newSize[1] *= windowPxSize[1]
        else:
            raise NotImplementedError
        return newSize[0],newSize[1]

    def _closeWindow(self,tkWindow : tk.Tk, returnData, succes : bool  ):
        tkWindow.quit()
        tkWindow.destroy()
        returnData.succes = succes

    def _doSpriteOp(self,varToEdit,otherCommands,sceneAssetinstanceId,spriteId,buttonId,windowSettings):#take vars from sprite, edit wished vars, and if wished, toggle
        to = self.sceneAssets[sceneAssetinstanceId].clickOpp['VALUE_TO_SET']
        if (keysLen := len(varToEdit)) == 1:
            self.sceneReturnVars[varToEdit[0]] = to
        elif keysLen == 2:
            self.sceneReturnVars[varToEdit[0]][varToEdit[1]] = to
        elif keysLen == 3:
            self.sceneReturnVars[varToEdit[0]][varToEdit[1]][varToEdit[2]] = to
        else:
            raise NotImplementedError("Should be obvious from the code what needs to be done")
        if otherCommands != None:
            if 'toggleSelf' in otherCommands:
                self.sceneAssets[sceneAssetinstanceId].toggle(0)
                self.sceneAssets[sceneAssetinstanceId].updateAfterToggle()
                img, posx, posy = self._createSprite(self.window,windowSettings,self.sceneAssets[sceneAssetinstanceId])
                self.imgs[spriteId] = [img]
                self.poss[spriteId] = [posx,posy]
                self.buttons[buttonId].config(image=self.imgs[spriteId])
                self.window.update_idletasks()
                
            else:
                raise NotImplementedError("this button command has not been implemented yet")
        pass

    def _toggleSelf(self,button,sprite,window,img2Change,pos2Change,windowSettings,returnData):
        sprite.toggle
        pass

    def _createSprite(self,tkWindow : tk.Tk, windowSettings : dict, sprite):
        img = Image.open(sprite.imgPath)
        posx,posy = self._posConverter(tkWindow,windowSettings,sprite.pos)
        sizex,sizey = self._sizeConverter(tkWindow,windowSettings,sprite.size)
        img = img.resize([int(sizex),int(sizey)], Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        
        return img, posx, posy
    
    def __init__(self):
        self.sceneReturnVars = 0
        self.imgs = []
        self.poss = []
        self.sceneAssets = []
        self.buttons = []
        self.window = tk.Tk()
    def display(self,scene):
        try:
            self.window.destroy()
        except tk.TclError:
            pass
        self.window = tk.Tk()
        returnData = UIReturnData()
        if scene.windowSettings['FULLSCREEN'] == True:
            scene.windowSettings['RESOLUTION'] = self.window.winfo_screenheight()
        self.window, canvas = self._makeCanvas(self.window, scene.windowSettings)
        self.imgs = []
        self.poss = []
        texts = []
        commands = []
        entryVars = {}
        usedFont = font.Font(size=30)
        self.sceneReturnVars = scene.returnVars
        self.sceneAssets = []
        for i,a in enumerate(scene.assets):
            prevId = a.instanceId
            a.instanceId = len(self.sceneAssets)
            self.sceneAssets.append(a)
            if a.type == 'sprite':
                #if a.name
                spriteId = len(self.imgs)
                buttonId = len(self.buttons)
                img, posx, posy = self._createSprite(self.window,scene.windowSettings,a)
                self.poss.append([posx,posy])
                self.imgs.append([img])
                if a.clickOpp:
                    commands = []
                    for c in a.clickOpp['COMMANDS']:
                        commands.append(eval('self._'+c))
                    button = 0
                    var2ChangeKeys = copy(a.clickOpp['VAR_TO_CHANGE'])
                    instance = prevId#!is actually used below in the eval function
                    for i in range(len(var2ChangeKeys)):
                        var2ChangeKeys[i] = eval(f'f"""{var2ChangeKeys[i]}"""')
                        try:
                            int(var2ChangeKeys[i])
                            var2ChangeKeys[i] = int(var2ChangeKeys[i])
                        except:
                            pass
                    button = tk.Button(
                        self.window,
                        image=self.imgs[-1],
                        command=partial(
                            self._doSpriteOp,*[
                                var2ChangeKeys,
                                a.clickOpp['COMMANDS'],
                                self.sceneAssets[-1].instanceId,
                                spriteId,
                                buttonId,
                                scene.windowSettings
                            ]),
                        borderwidth=0,
                        bg='black')
                    self.buttons.append(button)
                    canvas.create_window(self.poss[-1][0],self.poss[-1][1], window=self.buttons[-1])
                else:    
                    canvas.create_image(self.poss[-1][0],self.poss[-1][1],image=self.imgs[-1])
                canvas.pack()
            elif a.type == 'button':
                args = list(a.cmdArgs.values())
                texts.append(a.text)
                if a.command != None:
                    commands.append(partial(eval('self._'+a.command),*[self.window,returnData,args[0]]))
                    self.buttons.append(tk.Button(self.window, text=texts[-1], command=commands[-1]))
                else:
                    self.buttons.append(tk.Button(self.window, text=texts[-1]))
                self.buttons[-1]['font'] = usedFont
                w,h = 10,10
                if 'e' in a.allignment:
                    w = scene.windowSettings['RESOLUTION']/scene.windowSettings['RATIO'][1]*scene.windowSettings['RATIO'][0]-10
                elif 'w' in a.allignment:
                    pass
                else:
                    w = scene.windowSettings['RESOLUTION']/scene.windowSettings['RATIO'][1]*scene.windowSettings['RATIO'][0]/2
                if 's' in a.allignment:
                    h = scene.windowSettings['RESOLUTION']-10
                elif 'n' in a.allignment:
                    pass
                else:
                    h = scene.windowSettings['RESOLUTION']/2
                canvas.create_window(w, h, anchor=a.allignment, window=self.buttons[-1])
                canvas.pack()
            elif a.type == 'entry':
                main = tk.PanedWindow(canvas, width=scene.windowSettings['RESOLUTION']/scene.windowSettings['RATIO'][1]*scene.windowSettings['RATIO'][0], height=scene.windowSettings['RESOLUTION'], orient=tk.HORIZONTAL)
                frame1 = tk.Frame(canvas, height=40, width=200)
                frame2 = tk.Frame(canvas, height=40, width=200)
                entryVars[a.targetVar] = _entryVar(a.expectedDataType)
                tk.Label(frame1, text=a.text, font=usedFont).grid(row=a.row, column=a.column)
                tk.Entry(frame2, textvariable=entryVars[a.targetVar], font=usedFont).grid(row=a.row, column=a.column+1)
                main.add(frame1)
                main.add(frame2)
                main.pack()
            else:
                raise NotImplementedError("this type of asset is not implemented yet")
        tk.mainloop()
        for k in entryVars.keys():
            self.sceneReturnVars[k] = entryVars[k].get()
            if entryVars[k].expectedType == 'int':
                try:
                    self.sceneReturnVars[k] = int(self.sceneReturnVars[k])
                except:
                    returnData.succes = False
            elif entryVars[k].expectedType == 'float':
                try:
                    self.sceneReturnVars[k] = float(self.sceneReturnVars[k])
                except:
                    returnData.succes = False
            elif entryVars[k].expectedType == 'bool':
                try:
                    self.sceneReturnVars[k] = bool(self.sceneReturnVars[k])
                except:
                    returnData.succes = False
            elif entryVars[k].expectedType == 'str':
                try:
                    self.sceneReturnVars[k] = str(self.sceneReturnVars[k])
                except:
                    returnData.succes = False
        returnData.returnVar = self.sceneReturnVars
        return returnData

