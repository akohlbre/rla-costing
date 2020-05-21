#!/usr/bin/python3
import math
import csv
from argparse import ArgumentParser
margin = 10.0 # percentage points
rlaType = "comparison"
riskLimit = 10.0
hourlyRate = 20.0 # $
isPilot = True
contestsCount = 1.0
numberLocations = 1.0
turnoutCount = 500000

scanTime = 0.00295204
executionTime = 0.06297962
createManifestTime = 0.00004796
generateSeedTime = 0.93
consumablesPerLocation = 50 #TODO confirm

PILOT_PENALTY = 0.3 #TODO temp value, confirm.

def getInputs(inputFile):
    try:
        csvFile = open(inputFile)
    except:
        print("WARNING: no input file found, using default values for all variables")
        return True #use default variables if no file found
    with csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            key = row[0].lower()
            value = row[1].lower()
            if key == "number of ballots":
                try:
                    global turnoutCount
                    turnoutCount = float(value)
                except:
                    print(f'Couldn\'t parse the number of ballots: {value}')
                    return false
            elif key == "margin":
                try:
                    global margin
                    margin = float(value)
                except:
                    print(f'Couldn\'t parse the margin: {value}')
            elif key == "rla type":
                global rlaType
                rlaType = value
            elif key == "hourly wage":
                try:
                    global hourlyRate
                    hourlyRate = float(value)
                except:
                    print(f'Couldn\'t parse the hourly rate: {value}')
                    return false
            elif key == "pilot":
                global isPilot
                isPilot = (value == "yes")
            elif key == "number of contests":
                try:
                    global contestsCount
                    contestsCount = float(value)
                except:
                    print(f'Couldn\'t parse the number of contests: {value}')
                    return false
            elif key == "number of locations":
                try:
                    global numberLocations
                    numberLocations = float(value)
                except:
                    print(f'Couldn\'t parse the number of locations: {value}')
                    return false
            # secret configurables
            elif key == "scanTime".lower():
                try:
                    global scanTime
                    scanTime = float(value)
                except:
                    print(f'Couldn\'t parse scanTime: {value}')
                    return false
            elif key == "createManifestTime".lower():
                try:
                    global createManifestTime
                    createManifestTime = float(value)
                except:
                    print(f'Couldn\'t parse createManifestTime: {value}')
                    return false
            elif key == "executionTime".lower():
                try:
                    global executionTime
                    executionTime = float(value)
                except:
                    print(f'Couldn\'t parse executionTime: {value}')
                    return false
            elif key == "generateSeedTime".lower():
                try:
                    global generateSeedTime
                    generateSeedTime = float(value)
                except:
                    print(f'Couldn\'t parse generateSeedTime: {value}')
                    return false
            elif key == "consumablesPerLocation".lower():
                try:
                    global consumablesPerLocation
                    consumablesPerLocation = float(value)
                except:
                    print(f'Couldn\'t parse consumablesPerLocation: {value}')
                    return false
        return True

def validateInputs():
    if (not (rlaType == "polling" or rlaType == "comparison")):
        print(f'RLA type invalid: must be "polling" or "comparison", is {rlaType}')
        return False
    if not (0 <= margin and margin <=100):
        print(f'margin is invalid: must be between 0 and 100, is {margin}')
        return False
    if not (1 <= contestsCount and contestsCount < 100):
        print(f'number of contests is invalid, must be between 1 and 99, is {contestsCount}')
        return False
    if not (0 < riskLimit and riskLimit < 30):
        if (riskLimit > 30 and riskLimit < 100):
            print(f'Nonstandard risk limit({riskLimit}%, going ahead anyway')
        else:
            print(f'risk limit is invalid, must be between 0 and 100, is {riskLimit}')
            return False
    print("Calculating costs with these settings:")
    print(f'An election with {turnoutCount} ballots where the margin is {margin} points.')
    pilotString = "pilot " if isPilot else ""
    print(f'Conducting a {pilotString}ballot-{rlaType} audit on {contestsCount} contest(s) with a risk limit of {riskLimit} percent')
    print(f'and employees paid ${hourlyRate} per hour.')
    print("\n")
    return True

def laborGenerateSeed():
    return generateSeedTime * numberLocations

def laborCreateManifest():
    return turnoutCount * createManifestTime

def laborScan():
    if (rlaType == "polling"): return 0
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
    sample = math.ceil(sample)
    print(f'expected sample size in each location is {sample} ballots')
    return numberLocations * min(sample, turnoutCount/numberLocations)

# adapted from https://www.stat.berkeley.edu/~stark/Vote/ballotPollTools.htm
def calculateSampleSizePolling():
    s = 0.5 + (margin/100.0) # winner's reported vote share
    zw = math.log(2.0*s)
    zl = math.log(2.0 * (1-s))
    asn = math.ceil((math.log(1.0/(riskLimit/100.0)) + zw/2.0) / (s * zw + (1-s)*zl))

    print(f'expected sample size in each location is {asn} ballots')
    return numberLocations * min(asn, turnoutCount/numberLocations)

def laborExecute():
    if (rlaType == "polling"):
        sampleSize = calculateSampleSizePolling()
    else:
        assert(rlaType == "comparison")
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

def consumablesCosts():
    return consumablesPerLocation * numberLocations

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
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", metavar="FILE",
            help="input CSV file to read", default="state.csv")
    args = parser.parse_args()
    getInputs(args.filename)
    assert(validateInputs())
    print("Calculating total cost of audit:")
    print("$", calculateTotalCost())
