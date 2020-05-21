#!/usr/bin/python3
import json
#TODO general error checking on files, configuration
scannerPerLocation = 1.5
verifierFile = "verifier-search.json"
#state = "Virginia"
#state = "Georgia"
state = "Texas"
#state = "Nevada"
#state = "Louisiana"
#state = "Mississippi"
#state = "Tennessee"
#state = "Indiana"
#state = "New Jersey"
#state = "Kentucky"
#state = "Kansas"
rlaType = "comparison"

# TODO - settle on values for all these constants
scannersPerLocation = 1.0
scannerCost = 3000.0
bmdsPerLocation = 3.0 #TODO
# median voters/precinct is 870, average is 1332
bmdCost = 2500.0
upgradeType = "bmd"
numberUnreachedPrecincts = 20.0
cvrMachinesPerLocation = 3.0
cvrMachineCost = 10000.0
cvrScannersPerLocation = 0.25
cvrScannerCost = 100000.0

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

def calculateIncapablePrecincts(verifierData):
    stateMachines = [record for record in verifierData["codes"]
            if record["state_name"] == state]
    countyRecords = collectMatching(stateMachines)
    counties = {}
    for county in countyRecords:
        counties[county] = {
                "voters": countyRecords[county][0]["current_reg_voters"],
                "precincts": countyRecords[county][0]["precincts"],
                "capabilities": set([indiv["marking_method"] for indiv in countyRecords[county]])
                }
    incapableCounties = [counties[county]
            for county in counties\
            if counties[county]["capabilities"].isdisjoint(requirements)]
    totalIncapablePrecincts = 0
    for incCounty in incapableCounties:
        totalIncapablePrecincts += int(incCounty["precincts"])
    return totalIncapablePrecincts

def calculateUpgradeCostsPolling(incapablePrecincts):
    total = 0
    total += incapablePrecincts * scannersPerLocation * scannerCost
    if (upgradeType == "paper"):
        total += incapablePrecincts * bmdCost # usually req'd to have one for accessibility
    if (upgradeType == "bmd"):
        total += incapablePrecincts * bmdsPerLocation * bmdCost
    return total

def calculateUpgradeCostsComparison(incapablePrecincts, unreachedPrecincts):
    total = 0
    total += incapablePrecincts * cvrMachinesPerLocation * cvrMachineCost
    total += unreachedPrecincts * cvrScannersPerLocation * cvrScannerCost
    return total

with open(verifierFile) as verifierJson:
    verifierData = json.load(verifierJson)
    incapablePrecincts = calculateIncapablePrecincts(verifierData)
    cost = 0
    if (rlaType == "polling"):
        cost = calculateUpgradeCostsPolling(incapablePrecincts)
    else:
        assert(rlaType == "comparison")
        cost = calculateUpgradeCostsComparison(incapablePrecincts, numberUnreachedPrecincts)
    print(cost)
