from __future__ import print_function
import csv
import json
import os

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
    mesh_dict = construct_dict('../datasets/mtrees2018.csv') # name -> code
    mesh_dict_inverted = construct_dict('../datasets/mtrees2018_inverted.csv') # code -> name

    pateint_directory = '../datasets/patient_files'
    for filename in os.listdir(pateint_directory):
        if filename.endswith('.json'):
            full_name = os.path.join(pateint_directory, filename)
            with open(full_name) as patient_file:
                print('File: '+filename)
                patient_json = json.load(patient_file)
                keywords = patient_json['keywords']
                for keyword in keywords:
                    if keyword['valueIRI'].startswith('https://meshb.nlm.nih.gov'):
                        name = keyword['value']
                        code = mesh_dict[name]
                        mesh_branch = code.split('.')
                        mesh_branch_codes = ['.'.join(mesh_branch[:i]) for i in range(1,len(mesh_branch)+1)]
                        mesh_branch_names = [mesh_dict_inverted[code] for code in mesh_branch_codes]

                        top_level_code = mesh_branch_codes[0][0]
                        top_level_name = mesh_dict_inverted[top_level_code]
                        mesh_branch_names = [top_level_name] + mesh_branch_names
                        print(' -> '.join(mesh_branch_names))
                        # print('Key: ' + mesh_branch_names[0] + ', Value: ' + name)
                        print('\n')


        print('-----------------------------------------------------------------------------')


if __name__ == '__main__':
    main()
