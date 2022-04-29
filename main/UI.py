from HFJ_UI.UIHandler import UIInstance as window
from HFJ_UI import UIScenes as UIImporter
from HFJ_UI import UIHandler
from HFJ_UI.UIScenes import sceneCatalog
from configImporter.configImport import getConfig
configs = getConfig(__file__)

#import the HFJ method as a library

def init():
    UIHandler.init(configs)
    UIImporter.init(configs)

def drawScene(scene : str):
    testScene = window()
    testScene.display(sceneCatalog[scene.lower()])

def main():
    drawScene('testscene')
    
init()

if __name__ == '__main__':
    main()