
import re

from collections import defaultdict
from math import sqrt, acos, pi, log

print "Read Spatium.py"


def getFeatureSelectDict(classDict, notClassDict, method, minOcc=10):
    assert method == "GainRatio"
    wordScores = {}
    ac = sum(classDict.values())
    bd = sum(notClassDict.values())
    for aWord in classDict.keys():
        a = float(classDict[aWord])
        b = float(notClassDict[aWord])
        if a < minOcc or b < minOcc:
            continue
        c = float(ac-a)
        d = float(bd-b)
        aVal = calcGainRatio(a, b, c, d)
        wordScores[aWord] = aVal
    return wordScores


def calcGainRatio(a, b, c, d):
    n = a+b+c+d
    summand1 = a/n * log((a*n)/((a+b)*(a+c)), 2)
    summand2 = c/n * log((c*n)/((a+c)*(c+d)), 2)
    return summand1 + summand2


def featureSelection(sampleWList, wLen, filterHapax=True):
    ky, val = sampleWList.keys(), sampleWList.values()
    val, ky = zip(*sorted(zip(val, ky), reverse=True))
    if filterHapax and val[0] != val[-1]:
        aWordList = [ky[i] for i in xrange(min(wLen, len(ky)))
                     if val[i] > val[-1]]
    else:
        aWordList = [ky[i] for i in xrange(min(wLen, len(ky)))]
    return aWordList


def freqByList(wLists, aWordList):
    newWLists = []
    for aProfile in wLists:
        newWLists.append([aProfile[key] for key in aWordList])
    return newWLists


def convertToRelFreq(wLists):
    newWLists = []
    for aProfile in wLists:
        authorProfile = defaultdict(float)
        scaling = sum(aProfile.values()) / 1000.0
        for key in aProfile.keys():
            authorProfile[key] = aProfile[key]/scaling
        newWLists.append(authorProfile)
    return newWLists


def calcDiff(sampleFreq, listOfProfileFreq, method):
    assert method in ["Canberra", "Clark"]
    differences = []
    for profFreq in listOfProfileFreq:
        differences.append(calcDist(profFreq, sampleFreq, method))
    return differences



def calcDist(profFreq, sampleFreq, method):
    assert method in ["Canberra", "Clark"]
    profFreq = [max(x, 0.000001) for x in profFreq]
    sampleFreq = [max(x, 0.000001) for x in sampleFreq]
    ln = xrange(len(profFreq))
    diff = [abs(sampleFreq[i] - profFreq[i]) for i in ln]
    s = [sampleFreq[i] + profFreq[i] for i in ln]
    if method == "Canberra":
        q = [diff[i]/s[i] for i in xrange(len(diff))]
        return sum(q)
    elif method == "Clark":
        q = [(diff[i]/s[i])**2 for i in xrange(len(diff))]
        return sum(q)**0.5
    else:
        print method, "not yet implemented"
        assert False


def distance(profiles, sampleWList, aWordList, method):
    relProfiles = convertToRelFreq(profiles)
    relSamples = convertToRelFreq([sampleWList])

    listOfProfileFreq = freqByList(relProfiles, aWordList)
    listOfSampleFreq = freqByList(relSamples, aWordList)[0]

    return calcDiff(listOfSampleFreq, listOfProfileFreq, method)
