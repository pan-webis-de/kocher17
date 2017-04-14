# -*- coding: utf-8 -*-

import os
import re
import string

from collections import defaultdict

print "Read WordDict.py"


def getListPAN(aPath):
    aListPANAP = []
    for f in os.listdir(aPath):
        if ".xml" in f:
            aListPANAP.append(aPath + "/" + f)

    names = [re.findall(r'/(.*?)\.xml', s)[0] for s in aListPANAP]
    names, aListPANAP = zip(*sorted(zip(names, aListPANAP)))

    return aListPANAP


def getTruth(aPath):
    truthAP = fetchDocuments(aPath + '/truth.txt')
    names = [re.findall(r'^(.*?):::', s)[0] for s in truthAP[0]]
    names, truthAP = zip(*sorted(zip(names, truthAP[0])))
    return truthAP


# extract all doc from aFileName and returns its content in a List
def fetchDocuments(aFileName):
    myFile = open(aFileName, 'r')
    aLine = myFile.readline()
    myLine = string.strip(string.join(string.split(aLine)))
    aListOfListOfLines = []
    aListOfLines = []
    while aLine:
        aListOfLines.append(myLine)
        aLine = myFile.readline()
        myLine = string.strip(string.join(string.split(aLine)))
    aListOfListOfLines.append(aListOfLines)
    myFile.close()
    return aListOfListOfLines


def saveDictToFile(aDict, filePath):
    with open(filePath, 'w') as outFile:
        for e in aDict:
            outFile.write(e + '¦@#' + str(aDict[e]) + "\n")


def loadDictFromFile(filePath):
    aDict = defaultdict(int)
    with open(filePath, 'r') as inFile:
        for line in inFile:
            t = line.split('¦@#')
            if len(t) != 2:
                print 'loadDictFromFile', t
                continue
            try:
                aDict[t[0]] = float(t[1])
            except ValueError:
                print 'loadDictFromFile', t, filePath
    return aDict


def saveAsModel(aPath, aListOfDict, aListOfNames):
    if not os.path.isdir(aPath + "/"):
        os.mkdir(aPath + "/")
    for i, aDict in enumerate(aListOfDict):
        filePath = aPath + "/" + aListOfNames[i]
        saveDictToFile(aDict, filePath)


def loadFromModel(aPath):
    aListOfDict = []
    names = os.listdir(aPath)
    names = [n for n in names if "truth.txt" not in n]
    names = [n for n in names if "featListGender.txt" not in n]
    names = [n for n in names if "featListLanguage.txt" not in n]
    for f in names:
        aListOfDict.append(loadDictFromFile(aPath + "/" + f))
    names = [re.findall(r'(.*?)\.xml', s)[0] for s in names]
    names, aListOfDict = zip(*sorted(zip(names, aListOfDict)))
    return aListOfDict


def saveFeatListAsModel(aPath, featList):
    if not os.path.isdir(aPath + "/"):
        os.mkdir(aPath + "/")
    genderFeatures = featList[0]
    languageFeatures = featList[1]
    with open(aPath + "/featListGender.txt", 'w') as outFile:
        for e in genderFeatures:
            outFile.write(e + "\n")
    with open(aPath + "/featListLanguage.txt", 'w') as outFile:
        for e in languageFeatures:
            outFile.write(e + "\n")


def loadFeatListFromModel(aPath):
    genderFeatures = []
    languageFeatures = []
    with open(aPath + "/featListGender.txt", 'r') as inFile:
        for line in inFile:
            if line[-1] == "\n":
                genderFeatures.append(line[:-1])
            else:
                genderFeatures.append(line)
    with open(aPath + "/featListLanguage.txt", 'r') as inFile:
        for line in inFile:
            if line[-1] == "\n":
                languageFeatures.append(line[:-1])
            else:
                languageFeatures.append(line)

    return [genderFeatures, languageFeatures]


def saveTruthAsModel(aPath, truth):
    if not os.path.isdir(aPath + "/"):
        os.mkdir(aPath + "/")
    with open(aPath + "/truth.txt", 'w') as outFile:
        for e in truth:
            outFile.write(e + "\n")


def loadTruthFromModel(aPath):
    truth = []
    with open(aPath + "/truth.txt", 'r') as inFile:
        for line in inFile:
            if line[-1] == "\n":
                truth.append(line[:-1])
            else:
                truth.append(line)

    return truth
