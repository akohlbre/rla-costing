#!/usr/bin/python3
import json
import csv
from argparse import ArgumentParser
#TODO general error checking on files, configuration
verifierFile = "verifier-search.json"
global state
state = "Virginia"
rlaType = "comparison"

# TODO - settle on values for all these constants
scannersPerLocation = 1.5
scannerCost = 3000.0
bmdsPerLocation = 3.0 #TODO
# median voters/precinct is 870, average is 1332
bmdCost = 2500.0
upgradeType = "paper"
boothsPerLocation = 3.0
boothCost = 159.0
cvrScannersPerCounty = 1.0
cvrScannerCost = 111500.0
precinctsPerLocation = 1.5
votersPerCvrScanner = 500000.0

requirements = set([
    ('All Mail Ballot Jurisdiction, Election Day Vote Centers: Ballot Marking Devices for all voters'),
    ('All Mail Ballot Jurisdiction, Election Day Vote Centers: Hand marked paper ballots and BMDs'),
    ('Ballot Marking Devices for all voters'),
    ('Hand marked paper ballots, BMDs for accessibility'),
    ('Vote Center Jurisdiction, Ballot Marking Devices for all voters'),
    ('Vote Center Jurisdiction, Hand marked paper ballots and BMDs'),
    ])

def collectMatching(stateRecords):
    stateCounties = {}
    for record in stateRecords:
        countyName = record["fips_10_digit"]
        if (countyName in stateCounties):
            stateCounties[countyName].append(record)
        else:
            stateCounties[countyName] = [record]
    return stateCounties

def calculateStateVoters(counties):
    population = 0
    for county in counties:
        population += int(counties[county]["voters"])
    return population

def calculateStateData(verifierData):
    stateMachines = [record for record in verifierData["codes"]
            if record["state_name"] == state]
    if (len(stateMachines) == 0):
        print(f'Couldn\'t find data on state {state}. Check spelling and capitalization')
        assert(False)
    countyRecords = collectMatching(stateMachines)
    counties = {}
    for county in countyRecords:
        counties[county] = {
                "voters": countyRecords[county][0]["current_reg_voters"],
                "precincts": countyRecords[county][0]["precincts"],
                "capabilities": set([indiv["marking_method"] for indiv in countyRecords[county]])
                }
    voters = calculateStateVoters(counties)
    incapableCounties = [counties[county]
            for county in counties\
            if counties[county]["capabilities"].isdisjoint(requirements)]
    totalIncapablePrecincts = 0
    for incCounty in incapableCounties:
        totalIncapablePrecincts += int(incCounty["precincts"])
    return (totalIncapablePrecincts, len(incapableCounties), voters)

def calculateUpgradeCostsPolling(incapableLocations):
    total = 0
    total += incapableLocations * scannersPerLocation * scannerCost
    total += incapableLocations * boothsPerLocation * boothCost
    if (upgradeType == "paper"):
        total += incapableLocations * bmdCost # usually req'd to have one for accessibility
    if (upgradeType == "bmd"):
        total += incapableLocations * bmdsPerLocation * bmdCost
    return total

def calculateUpgradeCostsComparison(incapableLocations, incapableCounties, voters):
    total = 0
    total += calculateUpgradeCostsPolling(incapableLocations)

    total += voters/votersPerCvrScanner * cvrScannerCost
    return total

def validateInputs():
    if not (rlaType == "polling" or rlaType == "comparison"):
        print(f'RLA type must be "polling" or "comparison", is {rlaType}')
        return False
    if not (upgradeType == "bmd" or upgradeType == "paper"):
        print(f'upgrade type must be "bmd" or "paper", is {rlaType}')
        return False
    print(f'Estimating upgrade costs for {state} to be able to conduct ballot-{rlaType} audits.')
    upgradeString = "paper" if upgradeType == "paper" else "BMDs"
    print(f'Counties that currently use DREs will instead use {upgradeString}.')
    return True

def getInputs(filename):
    global state
    global rlaType
    global upgradeType
    try:
        csvFile = open(filename)
    except:
        return True #use default variables if no file found
    with csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            key = row[0].lower()
            value = row[1].lower()
            if key == "state":
                state = row[1] #keep capitalization
            elif key == "rla type":
                rlaType = value
            elif key == "upgrade type":
                upgradeType = value
        return True

def readArgs():
    global state
    global rlaType
    global upgradeType
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename", metavar="FILE",
            help="file to read for state info", default="state.csv")
    parser.add_argument("-s", "--state", dest="state", metavar="STATE",
            help = "US state to run the model on", default=None)
    parser.add_argument("-r", "--rla-type", dest="rlaType", metavar="TYPE", default = "polling",
            help="which type (polling or comparison) of RLA to upgrade for")
    parser.add_argument("-u", "--upgrade-type", dest="upgradeType", metavar="TYPE", default = "paper",
            help="for counties with DREs, whether to upgrade to BMDs or paper")
    args = parser.parse_args()
    state = args.state
    rlaType = args.rlaType
    upgradeType = args.upgradeType
    getInputs(args.filename)
    assert(validateInputs())

if (__name__ == "__main__"):
    readArgs()
    with open(verifierFile) as verifierJson:
        verifierData = json.load(verifierJson)
        (incapablePrecincts, incapableCounties, voters) = calculateStateData(verifierData)
        incapableLocations = incapablePrecincts/precinctsPerLocation
        cost = 0
        if (rlaType == "polling"):
            cost = calculateUpgradeCostsPolling(incapableLocations)
        else:
            assert(rlaType == "comparison")
            cost = calculateUpgradeCostsComparison(incapableLocations, incapableCounties, voters)
        print(cost)
