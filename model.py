#!/usr/bin/python3
import math
# TODO -- all vars will be configurable in final version
population = 10000
turnoutPercent = 0.6
margin = 1.5 # percentage points
isBallotPolling = True
isBallotComparison = False
riskLimit = 5
hourlyRate = 20 # $
scanningRate = 200 # ballots per hour
boxSize = 400 # ballots per box
isPilot = True
#isPilot = False
contestsCount = 1
numberLocations = 3

turnoutCount = population * turnoutPercent

scanTime = 0.00295204
executionTime = 0.06297962
createManifestTime = 0.00004796
generateSeedTime = 0.93

PILOT_PENALTY = 0.3 #TODO temp value, confirm. make configurable?

#TODO add to this as we add inputs
def validateInputs():
    if (isBallotPolling == isBallotComparison): return False
    if not (0 <= turnoutPercent and turnoutPercent <= 1.0): return False
    if not (0 <= margin and margin <=100): return False
    if not (0 < riskLimit and riskLimit < 100): return False #TODO correct? should we sanity check?
    if not (1 <= contestsCount and contestsCount < 100): return False #TODO max num of contests?
    return True

def laborGenerateSeed():
    return generateSeedTime * numberLocations

def laborCreateManifest():
    return turnoutCount * createManifestTime

def laborScan():
    if (isBallotPolling): return 0
    return turnoutCount * scanTime

# taken from Stark 2010b, eqn 17
def calculateSampleSizeComparison():
    gamma = 1.03905 # inflator, this seems to be standard value
    k = 1.0 # number of 1-vote overstatements
    alpha = riskLimit / 100.0 # risk limit
    mu = margin / 100.0 # margin
    sample = -2.0 * gamma * \
            (math.log(alpha) + k * math.log(1.0 - (1.0/(2.0*gamma)))) * \
            (1.0/mu)
    return min(sample, turnoutCount)

# adapted from https://www.stat.berkeley.edu/~stark/Vote/ballotPollTools.htm
def calculateSampleSizePolling():
    s = 0.5 + (margin/100.0) # winner's reported vote share
    zw = math.log(2.0*s)
    zl = math.log(2.0 * (1-s))
    asn = math.ceil((math.log(1.0/(riskLimit/100.0)) + zw/2.0) / (s * zw + (1-s)*zl))
    return min(asn, turnoutCount)

def laborExecute():
    if (isBallotPolling):
        sampleSize = calculateSampleSizePolling()
    else:
        sampleSize = calculateSampleSizeComparison()
    return sampleSize * executionTime

laborFunctions = [laborGenerateSeed, laborCreateManifest, laborScan, laborExecute]
def calculateLaborCosts():
    totalHours = 0
    for laborFunction in laborFunctions:
        totalHours += laborFunction()
    totalLaborCost = totalHours * hourlyRate
    if (isPilot):
        totalLaborCost = totalLaborCost + totalLaborCost * PILOT_PENALTY
    return totalLaborCost

#TODO allow to be configured? add justification?
def consumablesCosts():
    return 50 * numberLocations

otherCostsFunctions = [consumablesCosts]

def calculateOtherCosts():
    total = 0
    for otherCostsFunction in otherCostsFunctions:
        total += otherCostsFunction()
    return total

costFunctions = [calculateLaborCosts, calculateOtherCosts]
    
def calculateTotalCost():
    total = 0
    for costFunction in costFunctions:
        total += costFunction()
    return total

if (__name__ == "__main__"):
    assert(validateInputs())
    #TODO should probably print out all the vars nicely to let user validate
    print("Calculating total cost of audit:")
    print("$", calculateTotalCost())
