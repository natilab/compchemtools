#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 13:12:08 2021

@author: nat
"""

#hcs_to_g09.py

"""Script for the processing of .HCS files into g09 input files. 
Conformation geometries are extracted from HCS files.
g09 job, method, route can be provided and g09 input files are created 
with the geometries.
Useful information from conformational search is extracted and written
into csv file.
"""

#%%modules

import os

import proc_hcs
from write_g09in import g09_job



#%% process hcs file, output list of molecules 

def get_mols(hcs_file, charge = 0, multiplicity = 1):
    """Processes hcs_file into a dictionary of molecule object for 
    each found conformation or conformer.
    """
    
    return proc_hcs.main(hcs_file, charge, multiplicity)




#%% generate g09_job

def create_g09ins(mol_list, nproc, mem, func, basis, job, chk = None):
    """mol_list: list of molecules as molecule objects.
    nproc: int, number of processors.
    mem: int, maximum memory (in GB).
    func: string, functional to use.
    basis: string, basis set to use.
    job: string, g09 job keywords and options as would appear 
    in input file.
    chk: string, name of chk file, default None (no chk generated).
    Out: list of g09_job objects, each one generated from a molecule 
    of the input list.
    """
    
    g09_jobs = []
    
    for molecule in mol_list:
        current_job = g09_job(molecule, nproc, mem, func, 
                 basis, job, chk)
        g09_jobs.append(current_job)
    
    return g09_jobs

    


#%% write g09 inputs in subfolder

def write_g09ins(g09_jobs, molname, extension, path):
    """g09_jobs: list of g09_job objects.
    molname: string, for main name of files.
    extension: string, extension of file ('.com', '.gjf').
    path: string, folder to work in. default: '.' (working directory).
    Out: writes g09 input files in subfolder within provided path.
    """
    try:
        os.mkdir(os.path.join(path, 'g09_inputs'))
    except FileExistsError:
        print('No directory created, g09_input already exists.')
    
    for i, job in enumerate(g09_jobs):
        filename = molname + '_' + str(i+1) + extension
        job.write_input(os.path.join(path, 'g09_inputs', filename))


#%% write .csv file with conformational search info

def write_confSearch(mol_list, molname, path):
    """Writes csv file in provided path with conformer energy and found
    values for each one in the mol_list."""
    
    with open(os.path.join(path, molname+'.csv'), 'w') as f:
        f.write('conformer, energy, found \n')
        for i, molecule in enumerate(mol_list):
            f.write(f'conf {i+1}, {molecule.energy}, {molecule.found} \n')
    
    

#%% main function

def main(hcs_file, charge = 0, multiplicity = 1, nproc = 4, mem = 2, 
         func = 'B3LYP', basis = '6-31G*', job = '', chk = None, 
         molname = 'mol', extension = '.com', path = '.'):
    """Writes g09 inputs from hcs file and a csv file with
    energy and found values for each conformer."""
    
    mol_list = get_mols(hcs_file, charge, multiplicity)
    job_list = create_g09ins(mol_list, nproc, mem, func, basis, job, chk)
    write_g09ins(job_list, molname, extension, path)
    write_confSearch(mol_list, molname, path)


#%% 

if __name__ == '__main__':
    import argparse as ap
    parser = ap.ArgumentParser(prog = 'hcs_to_g09', 
                               description = 'Write g09 input files from .HCS file')
    
    parser.add_argument('input', type = str, 
                        help = 'input .HCS file')
    parser.add_argument('-c', '--charge', type = int, default = 0)
    parser.add_argument('-m', '--mult', type = int, default = 1,
                        help = 'multiplicity')
    parser.add_argument('-p', '--path', type = str, default = '.',
                        help = 'path to folder for writing files')
    parser.add_argument('-N', '--name', type = str, default = 'mol',
                        help = 'molecule name for generated input files')
    parser.add_argument('-o', '--out', type = str, default = '.com',
                        help = 'file extension for g09 files')
    parser.add_argument('-n', '--nproc', type = int, default = 4,
                        help = 'Number of processors to use')
    parser.add_argument('-M', '--mem', type = int, default = 4,
                        help = 'Memory to use, in GB')
    parser.add_argument('-f', '--func', type = str, default = 'B3LYP',
                        help = 'functional to use, must be accepted by g09')
    parser.add_argument('-b', '--basis', type = str, default = '6-31G*',
                        help = 'basis set to use')
    parser.add_argument('-j', '--job', type = str, default = '',
                        help = f'''g09 job keywords and options as would appear in input file.
                        Use single quotation marks around whole string when blankspaces are used.''')
    parser.add_argument('-C', '--chk', type = str, default = None,
                        help = 'name of chk file')
    
    args = parser.parse_args()
    
    main(hcs_file = args.input, charge = args.charge, multiplicity = args.mult,
         nproc = args.nproc, mem = args.mem, func = args.func, basis = args.basis,
         job = args.job, chk = args.chk, molname = args.name, extension = args.out,
         path = args.path)
    

    

    
    
    
     

