# -*- coding: utf-8 -*-

import getopt
import os
import re
import sys
from collections import Counter

from myEval import processAllAP, shortenAndRelativeDictsByList
from Spatium import getFeatureSelectDict
from WordDict import getListPAN, getTruth
from WordDict import saveAsModel, saveTruthAsModel, saveFeatListAsModel

theLanguage = ""
theNames = []

print "Read panAPtrain.py"


def mergeDicts(truthAP, allKnownDocs):
    theClasses = sorted(set(truthAP))
    listOfDicts = [Counter() for _ in theClasses]
    for anIndex, aKnown in enumerate(allKnownDocs):
        theClassIndex = theClasses.index(truthAP[anIndex])
        listOfDicts[theClassIndex] += aKnown
    return listOfDicts


def doFeatSelect(classDict, notClassDict, aFeatMethod, selectNumber, lowest):
    selectedDict = getFeatureSelectDict(classDict, notClassDict, aFeatMethod)
    ky, val = selectedDict.keys(), selectedDict.values()
    val, ky = zip(*sorted(zip(val, ky), reverse=True))
    if lowest:
        print "and 10 lowest for this class"
        return ky[:selectNumber]+ky[-10:]
    else:
        print "for this class"
        return ky[:selectNumber]


# print only when not imported
if __name__ == '__main__':
    print "The module panAPtrain.py was uploaded\n"

    inputFolder = ""
    outputFolder = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:")
    except getopt.GetoptError:
        print "panAPtrain.py -i <inFolder> -o <outFolder>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            inFolder = arg
        elif opt == "-o":
            outFolder = arg

    print "Input folder is", inFolder
    assert len(inFolder) > 0
    print "Output folder is", outFolder
    assert len(outFolder) > 0

    apFolder = sorted(os.listdir(inFolder))

    for c in apFolder:
        print "TRAINING", c
        inputFolder = inFolder + "/" + c
        outputFolder = outFolder + "/" + c
        truthAP = getTruth(inputFolder)
        aListPANAP = getListPAN(inputFolder)
        [allKnownDocs, theNames] = processAllAP(aListPANAP)
        theLanguage = c

        genderFeatures = []
        languageFeatures = []

        genderTruth = [re.findall(":::(female|male):::", e)[0] for e in truthAP]
        theClasses = sorted(set(genderTruth))
        listOfDicts = mergeDicts(genderTruth, allKnownDocs)
        for i in xrange(len(listOfDicts)):
            print "Gender", theClasses[i],
            print "GainRatio with 100 highest",
            classDict = listOfDicts[i]
            notClassDict = listOfDicts[:i]+listOfDicts[i+1:]
            if len(notClassDict) > 1:
                notClassDict = mergeDicts([0 for _ in notClassDict], notClassDict)
            notClassDict = notClassDict[0]
            newFeatures = doFeatSelect(classDict, notClassDict, "GainRatio", 100, False)
            genderFeatures.extend(newFeatures)

        languageTruth = [re.findall(":::(?:female|male):::(.*?)$", e)[0]
                         for e in truthAP]
        theClasses = sorted(set(languageTruth))
        listOfDicts = mergeDicts(languageTruth, allKnownDocs)
        for i in xrange(len(listOfDicts)):
            print "Language", theClasses[i],
            print "GainRatio with 70 highest",
            classDict = listOfDicts[i]
            notClassDict = listOfDicts[:i]+listOfDicts[i+1:]
            if len(notClassDict) > 1:
                notClassDict = mergeDicts([0 for _ in notClassDict], notClassDict)
            notClassDict = notClassDict[0]
            newFeatures = doFeatSelect(classDict, notClassDict, "GainRatio", 70, False)
            languageFeatures.extend(newFeatures)

        genderFeatures = sorted(set(genderFeatures))
        languageFeatures = sorted(set(languageFeatures))
        allFeatures = genderFeatures + languageFeatures
        allFeatures = sorted(set(allFeatures))

        allKnownDocs = shortenAndRelativeDictsByList(allKnownDocs, allFeatures)

        names = []
        for aFile in aListPANAP:
            names.append(aFile.replace(inputFolder, ""))
        saveTruthAsModel(outputFolder, truthAP)
        saveFeatListAsModel(outputFolder, [genderFeatures, languageFeatures])
        saveAsModel(outputFolder, allKnownDocs, names)
