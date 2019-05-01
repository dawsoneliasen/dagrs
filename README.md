# dagrs
dagrs is a Python module that turns a CSU DARS audit into a Directed Acyclic Graph, or DAG (DAG + DARS = dagrs).

## Installation
Clone the repository to get the dagrs source code.

## Usage
Save an audit html file in the dagrs/audits directory. Then, run the program on the audit from the command line. Specify the number of semesters you have left.
```
cd dagrs
python3 src/dagrs.py audit.html 4
```
The program may take several minutes to run - this is because course information must be downloaded from the CSU catalog, and there is a 1 second delay to reduce spam to the server. Once a course is downloaded, it does not have to be retrieved again, so successive runs will be faster.

A flowchart representing the suggested timeline of courses will be shown automatically, and saved in the output folder. 
