#! /bin/bash

echo 'Entire USA:'
./fit.py ../data/USA-flu.csv USA.%ILI | egrep 'beta|min|init|max|season|mean|stdv'
echo 'HHS Region 4:'
./fit.py ../data/USA-flu.csv R04.%ILI | egrep 'mean|stdv'
echo 'Tennessee:'
./fit.py ../data/TN-flu.csv   TN.%ILI | egrep 'mean|stdv'
echo 'TN District 10:'
./fit.py ../data/TN-flu.csv  D10.%ILI | egrep 'mean|stdv'
