from __future__ import print_function
import csv
import json
import os
import pandas
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('configuration', help = 'Configuration file of the request')
parser.add_argument('--patient_directory', help = 'Directory of the patient .json files.', default = '../datasets/patient_files')
parser.add_argument('--mapping', help = 'File with the mesh term mapping (values to integers).', default = '../datasets/mesh_mapping.json')
parser.add_argument('--output', help = 'The output csv to be created.', default = '../datasets/data.csv')
args = parser.parse_args()



def construct_dict(csv_file, delimiter=';'):
    with open(csv_file) as f:
        reader = csv.reader(f, skipinitialspace=True, delimiter=delimiter)
        d = dict(reader)
        return d

def mesh_tree_depth(code):
    if len(code) == 1:
        return 0
    else:
        return code.count('.') + 1

def main():
    configuration = json.load(open(args.configuration))
    # MESH_TERMS = ['Persons', 'Diseases']
    MESH_TERMS = [configuration['attribute']]
    mesh_dict = construct_dict('../datasets/mtrees2018.csv') # name -> code
    mesh_dict_inverted = construct_dict('../datasets/mtrees2018_inverted.csv') # code -> name
    mesh_mapping = json.load(open(args.mapping))
    direct_children = {}

    for term in MESH_TERMS:
        code = mesh_dict[term]
        depth = mesh_tree_depth(code)
        children = [mesh_dict_inverted[key] for key in mesh_dict_inverted.keys() if key.startswith(code) and mesh_tree_depth(key) == depth + 1]
        direct_children[term] = children


    df = pandas.DataFrame(columns = ['Id'] + MESH_TERMS)
    id = 0
    for filename in os.listdir(args.patient_directory): # for each patient file
        patient_values = {key: [] for key in MESH_TERMS} # initialize values to empty lsit, for every term in MESH_TERMS
        if filename.endswith('.json'):
            full_name = os.path.join(args.patient_directory, filename)
            with open(full_name) as patient_file:
                # print('File: '+filename)
                patient_json = json.load(patient_file)
                keywords = patient_json['keywords']
                for keyword in keywords: # for each one of the patient's keywords
                    if keyword['valueIRI'].startswith('https://meshb.nlm.nih.gov'):
                        name = keyword['value']
                        code = mesh_dict[name]
                        mesh_branch = code.split('.')
                        mesh_branch_codes = ['.'.join(mesh_branch[:i]) for i in range(1,len(mesh_branch)+1)]
                        mesh_branch_names = [mesh_dict_inverted[code] for code in mesh_branch_codes]

                        top_level_code = mesh_branch_codes[0][0]
                        top_level_name = mesh_dict_inverted[top_level_code]
                        mesh_branch_names = [top_level_name] + mesh_branch_names
                        # print(' -> '.join(mesh_branch_names))
                        for term in MESH_TERMS:
                            children = direct_children[term]
                            value = set(mesh_branch_names).intersection(children)
                            if len(value) > 0:
                                value = str(list(value)[0])
                                mapped_value = mesh_mapping[term][value]
                                if patient_values[term] == []:
                                    patient_values[term] = [mapped_value]
                                else:
                                    patient_values[term].append(mapped_value)

        # print(patient_values)
        # print('-----------------------------------------------------------------------------')
        for term in MESH_TERMS:
            for value in patient_values[term]:
                df = df.append({'Id' : id, term : value}, ignore_index = True)
        id += 1

    df.fillna(-1, inplace = True)
    df = df.astype(int)
    df.to_csv(args.output, sep = ';', index = False)
    print('CSV file generated at ' + args.output)

if __name__ == '__main__':
    main()
