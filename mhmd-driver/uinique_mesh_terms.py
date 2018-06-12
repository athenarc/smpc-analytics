from __future__ import print_function
import csv
import json
import os
import pandas
import argparse
import itertools
from huepy import *
import sys
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument('patients_file', help = 'Json file with patient metadata.')
parser.add_argument('--output', help = 'The output csv to be created.', default = 'unique.json')
parser.add_argument('--verbose', help = 'See verbose output', action = 'store_true')
args = parser.parse_args()


def main():
    d = {}
    print(run('Rading all JSON Entries..'))
    combined_patient_file = json.load(open(args.patients_file))
    length = len(combined_patient_file)
    if args.verbose:
        print(info('File contains ' + str(length) + ' entries.'))
    for patient_json in combined_patient_file:
        if args.verbose:
            identifier =  patient_json['identifier']['identifier']
            print(info('Patient ID: '+identifier))
        keywords = patient_json['keywords']
        for keyword in keywords: # for each one of the patient's keywords
            if keyword['valueIRI'].startswith('https://meshb.nlm.nih.gov'):
                name = keyword['value']
                if args.verbose:
                    print(info(name))
                if name not in d:
                    d[name] = 1
                else:
                    d[name] = d[name] + 1
        if args.verbose:
            print(yellow('-----------------------------------------------------------------------------------------------------'))

    with open(args.output, 'w') as outfile:
        json.dump(d,outfile)
    print(good('Output JSON file generated successfully at ' + args.output))

if __name__ == '__main__':
    main()
