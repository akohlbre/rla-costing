# rla-costing
Developing a cost model for Risk-Limiting Audits.

This was developed by Lauren Knight, Anne Kohlbrenner, and Corbin Stevens
as part of a project for WWS/COS 586 at Princeton University.
The associated written report is available upon request.

The models here should be considered works-in-progress that can be useful as guides, but
they are not authoritative references.

## Model of Operational Costs: `model.py`
### Running the Model
1. You can download the model and run it locally with [Python 3](https://www.python.org/downloads/).
Specify a filename with the `-f` flag to have the model use it as the input. If no file
is specified, the model will look for a file named `state.csv` and use it. If that file does not
exist, the model will use default values. See below for the input format

1. You can instead run the model on https://repl.it/languages/python3. It's probably easiest to
copy the contents of `model.py` into the white window on repl.it (rather than uploading a file to
repl.it). You can then change the input numbers at the top and click the "run" button to see the
output, which is the total cost in dollars.

### Input Format
To facilitate use by the greatest number of users, the input format is a csv file, which can
be written by hand or generated by any standard spreadsheet software. Only the first two
columns are significant. The names of fields go in the first column, and the values in the second.
Example:

|name of field|value|explanation|
| --- | --- | --- |
|number of ballots|500000|The total number of ballots expected. Example: 500000
|margin| 5|The margin, in percentage points. Example: 5
|RLA type|polling|The type of RLA, either "polling" or "comparison". Example: polling
hourly wage	|20	|The hourly rate for employees, in US dollars. Example: 20
pilot	|yes| Whether or not this is a pilot or first-time RLA, either "yes" or "no". Example: yes
number of contests |3| The number of individual contests that will be audited. Example: 3
number of locations |1| The number of separate locations that will conduct part of the audit. Example: 1

Capitalization doesn't matter, and there's no need to have a header row ("name of field".. above)
or a column for explanations, although neither is problematic.
The order of the rows does not matter.

## Model of Infrastructure Upgrade Costs: `infra.py`
### Running the Model
1. You can download the model and run it locally with [Python 3](https://www.python.org/downloads/).
Specify a filename with the `-f` flag to have the model use it as the input. If no file
is specified, the model will look for a file named `state.csv` and use it. Alternatively,
specify the three inputs with command line arguments, for example:
```./infra.py -s "New Jersey" -t polling -u paper```
to calculate the cost for NJ to upgrade to be able to conduct a ballot-polling audit,
opting to replace DREs with paper ballots.

### Input Format
To facilitate use by the greatest number of users, the input format is a csv file, which can
be written by hand or generated by any standard spreadsheet software. Only the first two
columns are significant. The names of fields go in the first column, and the values in the second.
Example:

|name of field|value|explanation|
| --- | --- | --- |
|state|New Jersey|
|RLA type|polling| which RLA type to calculate upgrade costs for, "polling" or "comparison"|
|Upgrade Type| paper|whether counties with DREs should be upgraded to "paper" or "bmd"s

Capitalization only matters for the state's name
, and there's no need to have a header row ("name of field".. above)
or a column for explanations, although neither is problematic.
The order of the rows does not matter.

### Other Dependencies
The model expects a file named `verifier-search.json` in the same directory. This file can be
downloaded from [Verfied Voting](https://www.verifiedvoting.org/verifier). A current version
is also located [in this repo](https://github.com/akohlbre/rla-costing/blob/master/verifier-search.json).
