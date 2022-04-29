from copy import copy, deepcopy
#import tkinter as tk
import os
from HFJ_UI.sceneAssetTypes import *
import ast

sceneCatalog = {}

def _setupSceneNames(config):
    global sceneCatalog
    scenes = config['UIScenes']
    for scn in scenes:
        sceneCatalog[scn.lower()] = scene()

def init(config):#must update all scenes with given info from config
    _setupSceneNames(config)
    cfg = config['UIScenes']
    for k in cfg.keys():
        kLower = k.lower()
        sceneCatalog[kLower].windowSettings = cfg[k]['WINDOWSETTINGS']
        if 'ASSETS' in cfg[k].keys():
            if 'SPRITES' in cfg[k]['ASSETS'].keys():
                for asset in cfg[k]['ASSETS']['SPRITES'].keys():
                    if 'OPTIONS' in cfg[k]['ASSETS']['SPRITES'][asset].keys():
                        defaultInfo = list(cfg[k]['ASSETS']['SPRITES'][asset]['OPTIONS'].keys())[0]
                        defaultInfo = cfg[k]['ASSETS']['SPRITES'][asset]['OPTIONS'][defaultInfo]
                        toggleAble = True
                        otherOptions = list(cfg[k]['ASSETS']['SPRITES'][asset]['OPTIONS'].keys())[1:]
                    else:
                        defaultInfo = cfg[k]['ASSETS']['SPRITES'][asset]
                        toggleAble = False
                    if 'INSTANCES' in cfg[k]['ASSETS']['SPRITES'][asset].keys():
                        instanceCount = cfg[k]['ASSETS']['SPRITES'][asset]['INSTANCES']
                        for i in range(instanceCount):
                            sceneCatalog[kLower].assets = copy(sceneCatalog[kLower].assets)
                            objIn = sprite(i,defaultInfo['POSITIONS'][i],defaultInfo['IMG_NAME'],defaultInfo['SIZE'],defaultInfo['CLICK_OPPERATION'],toggleAble)
                            sceneCatalog[kLower].assets.append(copy(objIn))
                            if toggleAble:
                                sceneCatalog[kLower].assets[-1].toggleAble = True
                                for j in range(len(otherOptions)):
                                    otherInfo = cfg[k]['ASSETS']['SPRITES'][asset]['OPTIONS'][otherOptions[j]]
                                    sceneCatalog[kLower].assets = copy(sceneCatalog[kLower].assets)
                                    sceneCatalog[kLower].assets[-1].pos_toggles.append(otherInfo['POSITIONS'][i])
                                    sceneCatalog[kLower].assets[-1].size_toggles.append(otherInfo['SIZE'])
                                    sceneCatalog[kLower].assets[-1].imgPath_togggles.append(os.path.join(sys.path[0],'UIAssets',otherInfo['IMG_NAME']))
                                    sceneCatalog[kLower].assets[-1].clickOpp_toggles.append(otherInfo['CLICK_OPPERATION'])
                    else:#!clickopp not implemented here, since not yet needed
                        sceneCatalog[kLower].assets = copy(sceneCatalog[kLower].assets)
                        sceneCatalog[kLower].assets.append(sprite(0,defaultInfo['POS'],defaultInfo['IMG_NAME'],defaultInfo['SIZE']))
                        if toggleAble:
                            sceneCatalog[kLower].assets[-1].toggleAble = True
                            for j in range(len(otherOptions)):#!not tested
                                otherInfo = cfg[k]['ASSETS']['SPRITES'][asset]['OPTIONS'][otherOptions[j]]
                                sceneCatalog[kLower].assets[-1].pos_toggles.append(otherInfo['POSITIONS'])
                                sceneCatalog[kLower].assets[-1].size_toggles.append(otherInfo['SIZE'])
                                sceneCatalog[kLower].assets[-1].imgPath_togggles.append(otherInfo['IMG_NAME'])
                    if 'VISIBLE' in defaultInfo.keys():#!depricated, needs updating if used
                        sceneCatalog[kLower].assets[-1].visible = defaultInfo['VISIBLE']
            if 'BUTTONS' in cfg[k]['ASSETS'].keys():
                for btn in cfg[k]['ASSETS']['BUTTONS'].keys():#!support for toggleable buttons not yet implemented
                    buttonInfo = cfg[k]['ASSETS']['BUTTONS'][btn]
                    cmd = None
                    cmdArgs = None
                    if 'COMMAND' in buttonInfo.keys():
                        cmd = buttonInfo['COMMAND']
                        cmdArgs = buttonInfo['ARGUMENTS']
                    sceneCatalog[kLower].assets = copy(sceneCatalog[kLower].assets)
                    sceneCatalog[kLower].assets.append(button(0,buttonInfo['ALLIGNMENT'],buttonInfo['TEXT'],cmd,cmdArgs))
            if 'ENTRIES' in cfg[k]['ASSETS'].keys():
                for ent in cfg[k]['ASSETS']['ENTRIES'].keys():
                    entryInfo = cfg[k]['ASSETS']['ENTRIES'][ent]
                    sceneCatalog[kLower].assets = copy(sceneCatalog[kLower].assets)
                    sceneCatalog[kLower].assets.append(entry(0,entryInfo['TEXT'],entryInfo['TARGETVARIABLE'],entryInfo['GRIDROW'],entryInfo['GRIDCOLLUMN'],entryInfo['DATATYPE']))
        if 'RETURNVARS' in cfg[k].keys():
            vars = {}
            for varName in cfg[k]['RETURNVARS']:
                if 'INSTANCES' in cfg[k]['RETURNVARS'][varName].keys():
                    vars[varName] = []
                    for i in range(cfg[k]['RETURNVARS'][varName]['INSTANCES']):
                        vars[varName].append(cfg[k]['RETURNVARS'][varName]['VALUE'])
                else:
                    vars[varName] = cfg[k]['RETURNVARS'][varName]['VALUE']
            sceneCatalog[kLower].returnVars = vars

def main():
    init()

if __name__ == '__main__':
    main()