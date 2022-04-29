import yaml
import os
from os import path

cfgs = {}
def getConfig(relativeFile : str):
    if path.isfile(relativeFile):
        relativeFile = os.path.dirname(relativeFile)
    _configFiles = [e for e in os.listdir(path.join(relativeFile,'ConfigFiles')) if e.split('.')[-1] == 'yaml']
    for cF in _configFiles:
        fileStream = open(path.join(relativeFile,'ConfigFiles',cF),'r',encoding='utf8')
        cfgs[''.join(cF.split('.')[:-1])] = yaml.safe_load(fileStream)
        print(f"imported config file {cF} with sections: {list(cfgs[''.join(cF.split('.')[:-1])].keys())}")
    return cfgs