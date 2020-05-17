#!/usr/bin/python3
# TODO -- all vars will be configurable in final version
population = 10000
turnoutPercent = 0.6
margin = 5 # percentage points
isBallotPolling = False
isBallotComparison = True
riskLimit = 5
hourlyRate = 20 # $
scanningRate = 200 # ballots per hour
boxSize = 400 # ballots per box
isPilot = True
contestsCount = 1

turnoutCount = population * turnoutPercent

sampleSize = 62 # TODO calculate, not const
pollingTimePerBallotSetup = 0.00004796 # TODO calculate, not const
pollingTimePerBallotExecute = False #TODO
comparisonTimePerBallotSetup = 0.00133333 # TODO calculate, not const
comparisonTimePerBallotExecute = 0.00047962 # TODO calculate, not const
pullSampleTime = 0.0337 #TODO
comparisonAdjudicateTime = 0.0111 #TODO
TIME_TO_GENERATE_SEED = 0.93 # TODO check
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
    return TIME_TO_GENERATE_SEED

def laborPrep():
    if (isBallotPolling):
        return pollingTimePerBallotSetup * turnoutCount
    assert(isBallotComparison)
    return comparisonTimePerBallotSetup * turnoutCount

def laborExecute():
    if (isBallotPolling):
        assert(False) #TODO
    assert(isBallotComparison)
    #TODO confirm below, probs sep into indiv sections
    return (turnoutCount * comparisonTimePerBallotExecute) + \
           (sampleSize   * pullSampleTime) + \
           (sampleSize   * comparisonAdjudicateTime)

laborFunctions = [laborPrep, laborExecute, laborGenerateSeed]
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
    return 50

#TODO allow to be configured? add justification?
def techCosts():
    return 250 + 199

infraFunctions = [consumablesCosts, techCosts]

def calculateInfrastructureCosts():
    total = 0
    for infraFunction in infraFunctions:
        total += infraFunction()
    return total

costFunctions = [calculateLaborCosts, calculateInfrastructureCosts]
    
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
