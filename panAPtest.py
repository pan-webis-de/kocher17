# -*- coding: utf-8 -*-

import getopt
import os
import re
import sys
from collections import Counter

from myEval import writeToXML, processAllAP, shortenAndRelativeDictsByList
from Spatium import calcDist, freqByList
from WordDict import getListPAN, getTruth
from WordDict import loadFromModel, loadTruthFromModel, loadFeatListFromModel

loo = 1  # TODO: eval loo=1, test loo=0

kOfNN = 13
method = "Clark"
theLanguage = ""
theNames = []

print "Read panAPtest.py"


def majorityVoting(theTruth, authorList):
    candidates = [theTruth[e] for e in authorList]
    theBest = candidates[0]
    theMax = -1
    for a in candidates:
        if candidates.count(a) > theMax:
            theMax = candidates.count(a)
            theBest = a
    return theBest


def runIt(allKnownDocs, allUnknownDocs, allFeatures):
    numKnown = len(allKnownDocs)
    print numKnown, "known"
    print len(allUnknownDocs), "unknown"

    [genderFeatures, languageFeatures] = allFeatures

    allKnownDocsGender = freqByList(allKnownDocs, genderFeatures)
    allUnknownDocsGender = freqByList(allUnknownDocs, genderFeatures)
    allKnownDocsLanguage = freqByList(allKnownDocs, languageFeatures)
    allUnknownDocsLanguage = freqByList(allUnknownDocs, languageFeatures)

    genderTruth = [re.findall(":::(female|male):::", e)[0] for e in truthAP]
    languageTruth = [re.findall(":::(?:female|male):::(.*?)$", e)[0]
                     for e in truthAP]

    distMatrixGender = [[0.0 for _ in allKnownDocsGender] for _ in allUnknownDocsGender]
    for unknownIdx, anUnknown in enumerate(allUnknownDocsGender):
        print theLanguage, "dist Gender", unknownIdx
        for knownIdx, aKnown in enumerate(allKnownDocsGender):
            dist = calcDist(anUnknown, aKnown, method)
            distMatrixGender[unknownIdx][knownIdx] = dist
    distMatrixLanguage = [[0.0 for _ in allKnownDocsLanguage] for _ in allUnknownDocsLanguage]
    for unknownIdx, anUnknown in enumerate(allUnknownDocsLanguage):
        print theLanguage, "dist Language", unknownIdx
        for knownIdx, aKnown in enumerate(allKnownDocsLanguage):
            dist = calcDist(anUnknown, aKnown, method)
            distMatrixLanguage[unknownIdx][knownIdx] = dist

    for check in xrange(len(allUnknownDocs)):
        distGender = distMatrixGender[check]
        _, authorList = zip(*sorted(zip(distGender, range(numKnown))))
        authorList = authorList[loo:kOfNN + loo]
        resultGender = majorityVoting(genderTruth, authorList)

        distLanguage = distMatrixLanguage[check]
        _, authorList = zip(*sorted(zip(distLanguage, range(numKnown))))
        authorList = authorList[loo:kOfNN + loo]
        resultLanguage = majorityVoting(languageTruth, authorList)

        results = [resultGender, resultLanguage]

        writeToXML(outputFolder, theNames[check], theLanguage, results)


# print only when not imported
if __name__ == '__main__':
    print "The module panAPtest.py was uploaded\n"

    inputFolder = ""
    outputFolder = ""
    inputRun = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:r:o:")
    except getopt.GetoptError:
        print "panAPtest.py -i <inFolder> -r <runInput> -o <outFolder>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            inFolder = arg
        elif opt == "-r":
            inRun = arg
        elif opt == "-o":
            outFolder = arg

    print "Input folder is", inFolder
    assert len(inFolder) > 0
    print "Input Run is", inRun
    assert len(inRun) > 0
    print "Output folder is", outFolder
    assert len(outFolder) > 0

    apFolder = sorted(os.listdir(inFolder))
    for c in apFolder:
        print "TEST", c, " with k =", kOfNN, "and distance =", method
        inputFolder = inFolder + "/" + c
        inputRun = inRun + "/" + c
        outputFolder = outFolder + "/" + c
        aListPANAP = getListPAN(inputFolder)
        [allUnknownDocs, theNames] = processAllAP(aListPANAP)
        theLanguage = c
        allKnownDocs = loadFromModel(inputRun)
        truthAP = loadTruthFromModel(inputRun)
        [genderFeatures, languageFeatures] = loadFeatListFromModel(inputRun)
        allFeatures = genderFeatures + languageFeatures
        allFeatures = sorted(set(allFeatures))
        allUnknownDocs = shortenAndRelativeDictsByList(allUnknownDocs, allFeatures)
        runIt(allKnownDocs, allUnknownDocs, [genderFeatures, languageFeatures])
