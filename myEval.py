
import os
import re
from collections import Counter

print "Read myEval.py"


def shortenAndRelativeDictsByList(allKnownDocs, allFeatures):
    shorter = []
    for aDict in allKnownDocs:
        newDict = {}
        scaling = 1.0*sum(aDict.values())
        for aFeat in allFeatures:
            newDict[aFeat] = aDict[aFeat]/scaling
        shorter.append(newDict)
    return shorter


def processAllAC(aListOfFile, ngram=0):
    wLists = []
    for aFile in aListOfFile:
        with open(aFile, 'r') as myFile:
            aText = myFile.read()
            aText = aText.lower()

        aText = re.sub(r"([\.,?!:\"\'\(\)])+", r" \1 ", aText)
        aText = re.sub(" +", " ", aText)
        if ngram>0:
            ngramList = [aText[i:i+ngram] for i in xrange(len(aText)-(ngram-1))]
            sampleWList = dict(Counter(ngramList))
        else:
            sampleWList = dict(Counter(aText.split()))
        wLists.append(sampleWList)
    return wLists


def processAllAP(aListOfFile):
    wLists = []
    theNames = []
    for aFile in aListOfFile:
        with open(aFile, 'r') as myFile:
            aText = myFile.read().lower()

        theNames.append(aFile.split("/")[-1][:-4])

        aSample = re.sub("<.?[a-z].*?>", "", aText)
        aSample = re.sub("<!\[cdata\[", "", aSample)
        aSample = re.sub("]]>\n", "", aSample)
        aSample = re.sub("\".*?>", "", aSample)
        aSample = re.sub("\t", " ", aSample)
        aSample = re.sub("\n+", " ", aSample)
        aSample = re.sub("&nbsp;", " ", aSample)
        aSample = re.sub("https?://t.co/\w+", " twitterlink ", aSample)
        aSample = re.sub("pic.twitter.com/\w+", " twitterpic ", aSample)
        aSample = re.sub("http://www.youtube.com/watch\?v=\w+",
                         " youtubelink ", aSample)
        aSample = re.sub("https?://[\S]+", " anylink ", aSample)
        aSample = re.sub("@\w+", " @username ", aSample)
        aSample = re.sub("[^&]#\w+", " #something ", aSample)
        aSample = re.sub(r"([\.,?!:\"\'\(\)-]+)", r" \1 ", aSample)
        aSample = re.sub(" +", " ", aSample)

        wLists.append(Counter(aSample.split()))
    return [wLists, theNames]


def writeToXML(aPath, aName, lang, results):
    if not os.path.isdir(aPath + "/"):
        os.mkdir(aPath + "/")
    s = "<author\tid=\"" + aName + "\"\n"
    s += "\tlang=\"" + lang + "\"\n"
    s += "\tvariety=\"" + results[1] + "\"\n"
    s += "\tgender=\"" + results[0] + "\"\n"
    s += "/>"
    with open(aPath + "/" + aName + ".xml", "w") as outFile:
        outFile.write(s)


def getMatches(aMatrix, aRowId, matches):
    for aColId in xrange(len(aMatrix[aRowId])):
        if aMatrix[aRowId][aColId][0] >= 2:  # at least 2 indications
            if aRowId not in matches:
                matches.append(aRowId)
            if aColId not in matches:
                matches.append(aColId)
                matches = getMatches(aMatrix, aColId, matches)
    return sorted(set(matches))


def writeClusterAndRank(aPath, aName, aMatrix, theNames):
    clusters = []
    unchecked = range(len(aMatrix))
    for anEl in unchecked:
        matches = getMatches(aMatrix, anEl, [])
        for aMatch in matches:
            del unchecked[unchecked.index(aMatch)]
        if len(matches):
            clusters.append(matches)
    clusters.extend([[x] for x in unchecked])

    if not os.path.isdir(aPath + "/" + aName + "/"):
        os.mkdir(aPath + "/" + aName + "/")

    with open(aPath + "/" + aName + "/clustering.json", "w") as outFile:
        outFile.write(getClusterText(clusters, theNames))

    noSingleCluster = [x for x in clusters if len(x) > 1]
    with open(aPath + "/" + aName + "/ranking.json", "w") as outFile:
        outFile.write(getRankingText(aMatrix, noSingleCluster, theNames))


def getClusterText(clusters, theNames):
    s = "[\n"
    for clusterId, aCluster in enumerate(clusters):
        s += "\t[\n"
        if len(aCluster) > 1:
            for aDoc in aCluster[:-1]:
                s += "\t\t{\"document\": \"" + theNames[aDoc] + "\"},\n"
            s += "\t\t{\"document\": \"" + theNames[aCluster[-1]] + "\"}\n"
        else:
            s += "\t\t{\"document\": \"" + theNames[aCluster[0]] + "\"}\n"
        if clusterId < len(clusters)-1:
            s += "\t],\n"
        else:
            s += "\t]\n"
    s += "]"
    return s


def getRankingText(aMatrix, noSingleCluster, theNames):
    isFirst = True
    s = "[\n"
    for aRowId in xrange(len(aMatrix)):
        for aColId in xrange(aRowId+1, len(aMatrix)):
            score = aMatrix[aRowId][aColId][1]
            if not isFirst:
                s += ",\n"
            s += "\t{\"document1\": \"" + theNames[aRowId] + "\",\n"
            s += "\t\"document2\": \"" + theNames[aColId] + "\",\n"
            s += "\t\"score\": " + str(score) + "}"
            isFirst = False
    s += "\n]"
    return s
