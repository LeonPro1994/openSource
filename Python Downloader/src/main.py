import os
import sys

frameworkPath = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'src')
sys.path.append(frameworkPath)

from src import coreLib

if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'config_files')
    testList = coreLib.generateTestListFromPath_(config_path)
    # testList = coreLib.listFilesAtPath_(config_path)
    # print(testList)
    for curTest in testList:
        curTestKeys = curTest.keys()
        fmProd = curTest['prod']
        fmWinVersion = curTest['winversion']
        fmVersion = curTest['version']
        fmProject = curTest['project']
        appCategory = curTest['category']
        filemakerVersion = curTest['fullname']
        fmInstaller = curTest['buildnum']

    x = coreLib.getBuildFromScm(project=fmProject, buildNum=fmInstaller, prod=fmProd, winVersion=fmWinVersion,bInstaller=True)
    assert x != 1, "Error while downloading build please investigate"
    coreLib.file_size_compare()
    coreLib.md5_compare()