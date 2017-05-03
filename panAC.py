# -*- coding: utf-8 -*-

import getopt
import os
import re
import sys
import time
from collections import Counter

from Spatium import featureSelection, distance
from myEval import processAllAC, writeClusterAndRank


print "Read panAC.py"

stdDevFactor = 1.64
print "stdDevFactor =", stdDevFactor


def getCandMatrix(distMatrix, stdDevFactor):
    rowAvgs = [sum(aRow)/(len(aRow)-1) for aRow in distMatrix]  # dist to itself is 0, so len-1
    rowStdDev = []
    for rowNo, aRow in enumerate(distMatrix):
        rowNoZero = aRow[:rowNo]+aRow[rowNo+1:]
        dev = sum([(aVal - rowAvgs[rowNo])**2 for aVal in rowNoZero])
        rowStdDev.append((dev/len(rowNoZero))**0.5)

    candMat = [[[0, 0, 0] for _ in distMatrix] for _ in distMatrix]
    for i in range(len(distMatrix)):
        currAvg = rowAvgs[i]
        currStdDev = rowStdDev[i]
        for j in range(len(distMatrix)):
            if i == j:
                continue
            currVal = distMatrix[i][j]
            if currVal < currAvg - stdDevFactor*currStdDev:
                candMat[i][j][0] += 1
                candMat[i][j][1] = (currAvg - currVal) / currStdDev
            candMat[i][j][2] = (currAvg - currVal) / currStdDev
    return candMat


def runIt(problemName):
    print problemName
    distMatrix = []

    for check in range(len(allKnownDocs)):
        if len(allKnownDocs[check]) < 5:
            print "\nunsolved", theNames[check], "\n"
            continue

        aWordList = featureSelection(allKnownDocs[check], 200, False)
        diffs = distance(allKnownDocs, allKnownDocs[check], aWordList, distMeasure)
        distMatrix.append(diffs)
    print "matrices done"

    # indication
    # if the distance from A to B is more than x standard deviations
    # below the average from A to any other
    horCandMat = getCandMatrix(distMatrix, stdDevFactor)

    # indication
    # if the distance from A to B is more than x standard deviations
    # below the average from any other to B
    distMatrixTransp = [[distMatrix[j][i] for j in range(len(distMatrix))]
                        for i in range(len(distMatrix))]
    vertCandMat = getCandMatrix(distMatrixTransp, stdDevFactor)

    candMat = [[[0, 0, 0] for _ in distMatrix] for _ in distMatrix]
    for i in range(len(candMat)):
        for j in range(i+1, len(candMat)):
            indications = (horCandMat[i][j][0] + vertCandMat[i][j][0] +
                           horCandMat[j][i][0] + vertCandMat[j][i][0])
            indicationWeight = (horCandMat[i][j][1] + vertCandMat[i][j][1] +
                                horCandMat[j][i][1] + vertCandMat[j][i][1])
            totalWeight = (horCandMat[i][j][2] + vertCandMat[i][j][2] +
                           horCandMat[j][i][2] + vertCandMat[j][i][2])
            candMat[i][j][0] = indications
            candMat[j][i][0] = indications
            candMat[i][j][1] = indicationWeight
            candMat[j][i][1] = indicationWeight
            candMat[i][j][2] = totalWeight
            candMat[j][i][2] = totalWeight

    maxVal1 = max([x[1] for aRow in candMat for x in aRow])
    maxVal1 = max(maxVal1, 1.0)
    maxVal2 = max([x[2] for aRow in candMat for x in aRow])
    minVal2 = min([x[2] for aRow in candMat for x in aRow])
    candMat = [[[x[0], x[1]/maxVal1, (x[2]-minVal2)/(maxVal2-minVal2)]
                for x in aRow] for aRow in candMat]
    candMat = [[[x[0], x[1]/5.0+0.8] if x[0] == 4 else x for x in aRow]
               for aRow in candMat]
    candMat = [[[x[0], x[1]/5.0+0.6] if x[0] == 3 else x for x in aRow]
               for aRow in candMat]
    candMat = [[[x[0], x[1]/5.0+0.4] if x[0] == 2 else x for x in aRow]
               for aRow in candMat]
    candMat = [[[x[0], x[1]/5.0+0.2] if x[0] == 1 else x for x in aRow]
               for aRow in candMat]
    candMat = [[[x[0], x[2]/5.0] if x[0] == 0 else x for x in aRow]
               for aRow in candMat]

    for aRow in candMat:
        for aTuple in aRow:
            assert len(aTuple) == 2

    print "calc done"

    writeClusterAndRank(outputFolder, problemName, candMat, theNames)


# print only when not imported
if __name__ == '__main__':
    print "The module panAC.py was uploaded\n"
    startTime = time.clock()

    inputFolder = ""
    outputFolder = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:")
    except getopt.GetoptError:
        print "panAC.py -i <inputFolder> -o <outputFolder>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-i":
            inputFolder = arg
        elif opt == "-o":
            outputFolder = arg

    print "Input folder is", inputFolder
    assert len(inputFolder) > 0
    print "Output folder is", outputFolder
    assert len(outputFolder) > 0
    distMeasure = "Canberra"

    acFolder = os.listdir(inputFolder)
    acFolder = sorted([x for x in acFolder if "problem" in x])

    for c in acFolder:
        theNames = sorted([f for f in os.listdir(inputFolder + "/" + c)])
        aListPANAP = [inputFolder + "/" + c + "/" + f for f in theNames]

        allKnownDocs = processAllAC(aListPANAP, ngram=6)
        runIt(c)

    print "\n done in %.2fs" % (time.clock() - startTime)
