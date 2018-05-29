import os
import sys
import json
import argparse
from huepy import *

parser = argparse.ArgumentParser()
parser.add_argument('file', help= 'Combined file with all JSON data')
parser.add_argument('--directory', help = 'Output directory where the individual files should be stored', default = './')
parser.add_argument('--verbose', help = 'See verbose output', action = 'store_true')
args = parser.parse_args()


def main():
    if args.verbose:
        print(run('Reading combined JSON file..'))
    combined = json.load(open(args.file))
    length = len(combined)
    if args.verbose:
        print(info('File contains ' + str(length) + ' entries.'))
        if args.directory == '.' or args.directory == './':
            print(run('Storing files in current directory..'))
        else:
            print(run('Storing files in ' + args.directory + ' directory..'))
    for patient in combined:
        identifier =  patient['identifier']['identifier']
        with open(os.path.join(args.directory, identifier + '.json'), 'w') as patient_file:
            json.dump(patient, patient_file)
    if args.verbose:
        print(good('Successfully stored ' + str(length) + ' individual JSON files.'))

if __name__ == '__main__':
    main()