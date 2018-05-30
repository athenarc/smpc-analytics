import os
import sys
import json
import argparse
from huepy import *

parser = argparse.ArgumentParser()
parser.add_argument('file', help= 'File with mtrees data (CSV or JSON)')
parser.add_argument('--mtrees', help = 'File with the mesh dictionary to be created (names to ids).', default = 'mhmd-driver/m.json')
parser.add_argument('--mtrees_inverted', help = 'File with the inverted mesh dictionary to be created (ids to names).', default = 'mhmd-driver/m_inv.json')
parser.add_argument('--verbose', help = 'See verbose output', action = 'store_true')
args = parser.parse_args()


def main():
    d = {}
    d_inv = {}
    if args.verbose:
        print(run('Reading mtrees file..'))
    if args.file.endswith('.json'):
        mtrees = json.load(open(args.file))
        length = len(mtrees)
        if args.verbose:
            print(info('File contains ' + str(length) + ' entries.'))
            print(run('Building dictionairies..'))
        for entry in mtrees:
            name = entry['name']
            # code = entry['code']
            id = entry['id']
            if name in d:
                d[name]['ids'].append(id)
            else:
                # d[name] = {'code': code, 'ids': [id]}
                d[name] = {'ids': [id]}

            if id not in d_inv:
                d_inv[id] = name
            else:
                print(bad(id+' not in d'))
    elif args.file.endswith('.csv'):
        with open(args.file, 'r') as input:
            if args.verbose:
                print(run('Building dictionairies..'))
            for line in input:
                name = line.split(';')[0]
                id = line.split(';')[1].strip()
                if name in d:
                    d[name]['ids'].append(id)
                else:
                    # d[name] = {'code': code, 'ids': [id]}
                    d[name] = {'ids': [id]}

                if id not in d_inv:
                    d_inv[id] = name
                else:
                    print(bad(id+' not in d'))
    else:
        print(bad('Wrong input file format'))
        print(bad('Expected a CSV or JSON file.'))

    # Add missing values -- Top tree level

    d['Anatomy'] = {'ids':['A']}
    d['Organisms'] = {'ids':['B']}
    d['Diseases'] = {'ids':['C']}
    d['Chemicals and Drugs'] = {'ids':['D']}
    d['Analytical, Diagnostic and Therapeutic Techniques, and Equipment'] = {'ids':['E']}
    d['Psychiatry and Psychology'] = {'ids':['F']}
    d['Phenomena and Processes'] = {'ids':['G']}
    d['Disciplines and Occupations'] = {'ids':['H']}
    d['Anthropology, Education, Sociology, and Social Phenomena'] = {'ids':['I']}
    d['Technology, Industry, and Agriculture'] = {'ids':['J']}
    d['Humanities'] = {'ids':['K']}
    d['Information Science'] = {'ids':['L']}
    d['Named Groups'] = {'ids':['M']}
    d['Health Care'] = {'ids':['N']}
    d['Publication Characteristics'] = {'ids':['V']}
    d['Geographicals'] = {'ids':['Z']}

    d_inv['A'] = 'Anatomy'
    d_inv['B'] = 'Organisms'
    d_inv['C'] = 'Diseases'
    d_inv['D'] = 'Chemicals and Drugs'
    d_inv['E'] = 'Analytical, Diagnostic and Therapeutic Techniques, and Equipment'
    d_inv['F'] = 'Psychiatry and Psychology'
    d_inv['G'] = 'Phenomena and Processes'
    d_inv['H'] = 'Disciplines and Occupations'
    d_inv['I'] = 'Anthropology, Education, Sociology, and Social Phenomena'
    d_inv['J'] = 'Technology, Industry, and Agriculture'
    d_inv['K'] = 'Humanities'
    d_inv['L'] = 'Information Science'
    d_inv['M'] = 'Named Groups'
    d_inv['N'] = 'Health Care'
    d_inv['V'] = 'Publication Characteristics'
    d_inv['Z'] = 'Geographicals'


    with open(args.mtrees, 'w') as outfile:
        json.dump(d, outfile)
    with open(args.mtrees_inverted, 'w') as outfile:
        json.dump(d_inv, outfile)

    print(good('Dictionaries successfully stored.'))

if __name__ == '__main__':
    main()