import os
import urllib
import hashlib
import sys
import requests
import xml.dom.minidom
from src import defaults_BJ
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from xml.dom.minidom import parse
from xml.dom.minidom import parse, parseString


file_status_info = {}
file_abs_path = None
urlLink = None

def listFilesAtPath_(rootdir):
    if os.path.exists(rootdir):
        fileList = []
        for root, subFolders, files in os.walk(rootdir):
            for file in files:
                fileList.append(os.path.join(root, file))
        return fileList


def generateTestListFromPath_(pathToTestConfigs):
    testConfigFileList = listFilesAtPath_(pathToTestConfigs)
    testConfigList = []
    for test in testConfigFileList:
        if test.endswith(".xml"):
            # print(test)
            testConfig = {}

            f = open(test, 'r')
            fileLines = f.read()
            f.close()
            installOptions = []
            dom = parseString(fileLines)

            for n in dom.documentElement.childNodes:
                if n.attributes != None:
                    if len(n.childNodes) == 1:
                        testConfig[n.nodeName] = n.childNodes[0].nodeValue
                    else:
                        subNodes = {}
                        for m in n.childNodes:
                            if m.attributes != None:
                                if m.nodeName not in subNodes.keys():
                                    subNodes[m.nodeName] = [m.childNodes[0].nodeValue]
                                else:
                                    subNodes[m.nodeName].append(m.childNodes[0].nodeValue)

                        testConfig[n.nodeName] = subNodes

            testConfigList.append(testConfig)

    return testConfigList


def getHTTPFile(url, localPath):
    rtn = 1
    f = None
    md5_value_on_server = None
    md5_value_on_local = None
    url = url.replace(" ", "%20")
    local_filename = url.split('/')[-1]
    try:
        data_lenth = 0
        old_num = 0
        f = urlopen(url)
        meta = f.info()
        file_size = meta['Content-Length']
        hash = hashlib.md5()
        r = requests.get(url, stream=True)
        with open(localPath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8092):
                if chunk:  # filter out keep-alive new chunks
                    hash.update(chunk)
                    f.write(chunk)
                    data_lenth += len(chunk)
                    f_num = float(float(data_lenth) / float(file_size))
                    if int(f_num) == 1:
                        print(']Done')
                    else:
                        f_num *= 100
                        if f_num != old_num:
                            sys.stdout.write(' ' * 100 + '\r')
                            sys.stdout.flush()
                            sys.stdout.write('\r%.2f%%' % f_num)
                            sys.stdout.write("Downloading[" + '>' * int(f_num) + "\b\b")
                            sys.stdout.flush()
                            old_num = f_num
        rtn = 0
        md5_value_on_server = hash.hexdigest()
    except HTTPError as e:
        print("HTTP Error: ", e.code, url)
    except URLError as e:
        print("URL Error: ", e.reason, url)
    except MemoryError as e:
        f = None
        try:
            f = urlopen(url)
            with open(localPath, "wb") as local_file:
                for x in f:
                    data = f.read(x)
                    hash.update(data)
                    local_file.write(x)
            rtn = 0
            md5_value_on_server = hash.hexdigest()
        except Exception as e:
            print("Memory Error: [", type(e).__name__, "] ", e)
    except Exception as e:
        print("ERROR: [", type(e).__name__, "] ", e)
    finally:
        if f: f.close()
    global  file_status_info
    file_status_info =  {'rtn':rtn,'file_size':file_size,'md5_value':md5_value_on_server}
    return file_status_info

def getBuildFromScm(project, buildNum, prod = "Adv", winVersion = "x64", bInstaller = True):
    fileName = None
    localBuildPath = os.path.join(defaults_BJ._localBuildPath,'Installers',project,buildNum)
    if os.path.exists(localBuildPath):
        import shutil
        shutil.rmtree(localBuildPath)
    if os.path.exists(localBuildPath) == False:
        if bInstaller:
            ver = defaults_BJ._projVer[project.lower()]
            build = buildNum[1]
            fileName = fileName = "Mac_Installer_%s.zip" % prod

    if fileName == None:
        print("cannot get %s build %s" % (project, buildNum))
        return False
    else:
        os.makedirs(localBuildPath)
        global urlLink,file_abs_path
        urlLink = os.path.join(defaults_BJ._httpBuildPathStructure % (defaults_BJ._projVer[project.lower()], buildNum.replace("x", "")),fileName)
        file_abs_path = os.path.join(localBuildPath, fileName)
        print("%s/%s" % (defaults_BJ._httpBuildPathStructure % (defaults_BJ._projVer[project.lower()], buildNum.replace("x", "")), fileName))
        getHTTPFile("%s/%s" % (defaults_BJ._httpBuildPathStructure % (defaults_BJ._projVer[project.lower()], buildNum.replace("x", "")),fileName), os.path.join(localBuildPath, fileName))

    return localBuildPath


def file_size_compare():
    site = urlopen(urlLink)
    meta = site.info()
    file_size_on_server = meta['Content-Length']
    file_size_on_local = os.stat(file_abs_path).st_size
    print('server_size:%s local_size:%s'%(file_size_on_server,file_size_on_local))
    if int(file_size_on_server) != int(file_size_on_local):
        print('File size compare failed')
        return False
    else:
        print('File size compare successfully')
        return True


def md5_compare():
    hash = hashlib.md5()
    with open(file_abs_path, 'rb') as f:
        for x in f:
            if x:
                hash.update(x)
    md5_value_on_client = hash.hexdigest()
    if file_status_info['md5_value'] != md5_value_on_client:
        print('Server MD5:%s  Client MD5:%s'%(file_status_info['md5_value'],md5_value_on_client))
        print('MD5 Check Failed')
        return False
    else:
        print('MD5 Check Success')
        return True

