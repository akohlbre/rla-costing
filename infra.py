#!/usr/bin/python3
import json
#TODO general error checking on files, configuration
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
