#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 16:33:51 2022

@author: nat
"""

# write_coordSI.py

"""Write .txt and/or .xyz file with information and coordinates from g09 output files 
in format for Supporting Information."""

#%% modules

import os

from proc_g09out import get_jobs, parse_file, check_term, error_term
from g09freq import get_freq, get_Nneg
from g09opt import get_SCF, get_molecule, split_opt, check_opt

#%% get functions from freq

def get_neg(parsed_freq_job):
    """Get number of negative frequencies from parsed frequency job output.
    Returns number as integer."""
    
    return get_Nneg(get_freq(parsed_freq_job))

def get_free_energy(parsed_freq_job):
    """Get free energy form parsed frequency job output.
    Returns energy value (Sum of electronic and thermal Free Energies)."""
    
    for line in parsed_freq_job:
        if 'Sum of electronic and thermal Free' in line:
            free_energy = float(line.split('=')[1])
            
    return free_energy    


    

#%% get-out functions, get all info from output

def get_out_freq(parsed_freq_job):
    """Get information from parsed frequency output to write SI.
    In: parsed freq output.
    Out: Energy, Free energy, Number of neg frequencies, 
    molecule (coordinates in a molecule class object)."""
    
    energy = get_SCF(parsed_freq_job)
    free_energy = get_free_energy(parsed_freq_job)
    n_neg = get_neg(parsed_freq_job)
    molecule = get_molecule(parsed_freq_job)
    
    
    return energy, free_energy, n_neg, molecule
    
def get_molecule_opt(parsed_opt_out):
    """Get molecule of final structure from optimization job.
    In: parsed opt output.
    Out: molecule (coordinates in a molecule class object)."""

    opt_steps = split_opt(parsed_opt_out)
    check_opt(parsed_opt_out)    

    molecule = get_molecule(opt_steps[-2]) # final molecule
    
    return molecule
    
    
def get_out_opt(parsed_opt_out):
    """Get information from parsed optimization output to write SI.
    In: parsed opt output.
    Out: Energy, 
    molecule (coordinates in a molecule class object)."""

    opt_steps = split_opt(parsed_opt_out)
    check_opt(parsed_opt_out)    
    
    energy = get_SCF(opt_steps[-2]) # final SCF energy
    molecule = get_molecule(opt_steps[-2]) # final molecule
    
    return energy, molecule

def get_out_sp(parsed_sp_out):
    """Get information from parsed single point output to write SI.
    In: parsed opt output.
    Out: Energy, 
    molecule (coordinates in a molecule class object)."""

    energy = get_SCF(parsed_sp_out) 
    molecule = get_molecule(parsed_sp_out) 
    
    return energy, molecule

#%% list_out

def list_freq_out(energy, free_energy, n_neg, molecule):
    """Get list output for SI for frequency job. 
    Out: list of strings, values separated by commas in each string."""
    
    freq_out = [f'Energy = {energy}',
                f'Free Energy = {free_energy}',
                f'Number of Imaginary Frequencies = {n_neg}',
                f'Geometry'] + molecule.tabXYZ()
    
    return freq_out

def list_scf_out(energy, molecule):
    """Get list output for SI for opt or SP job. 
    Out: list of strings, values separated by commas in each string."""    
    
    scf_out = [f'Energy = {energy}'] + molecule.tabXYZ()
    
    return scf_out


#%% job_to_list functions

def freq_to_list(parsed_freq_job):
    """Get output string list for writing SI from parsed frequency job."""
    energy, free_energy, n_neg, molecule = get_out_freq(parsed_freq_job)
   
    return list_freq_out(energy, free_energy, n_neg, molecule)

def opt_to_list(parsed_opt_job):
    """Get output string list for writing SI from parsed opt job."""
    
    energy, molecule = get_out_opt(parsed_opt_job)
    
    return list_scf_out(energy, molecule)

def sp_to_list(parsed_sp_job):
    """Get output string list for writing SI from parsed SP job."""
    
    energy, molecule = get_out_sp(parsed_sp_job)
    
    return list_scf_out(energy, molecule)

#%% g09out_to_list

def g09out_to_txt_list(pathin, g09out_name):
    """Get output string list for writing SI txt from g09 output file."""
    
    jobs, route = get_jobs(os.path.join(pathin, g09out_name))
    parsed_out = parse_file(os.path.join(pathin, g09out_name), jobs)
    
    
    if 'opt' in jobs:
        if 'freq' in jobs:
            # opt and freq job
            output_list = freq_to_list(parsed_out[1])
        else:
            # only opt job
            output_list = opt_to_list(parsed_out)
 
    elif 'freq' in jobs:
        # only freq job
        output_list = freq_to_list(parsed_out)
    
    else:
        # single point
        output_list = sp_to_list(parsed_out)
    
    return output_list

#%% g09out_to_xyz

def g09out_to_xyz(pathin, g09out_name):
    """Get output string list for writing SI xyz from g09 output file."""

    jobs, route = get_jobs(os.path.join(pathin, g09out_name))
    parsed_out = parse_file(os.path.join(pathin, g09out_name), jobs)

    if 'opt' in jobs:
        if 'freq' in jobs:
            # opt and freq job
            molecule = get_molecule(parsed_out[1])
        else:
            # only opt job
            molecule = get_molecule_opt(parsed_out)
    else:
        # freq or sp job
        molecule = get_molecule(parsed_out)
    
    xyz_out = [f'{molecule.natoms}', f'{g09out_name}'] + molecule.strXYZ()
    
    return xyz_out
    
    
#%% write txt

def write_txt(path, out_filename, results):
    with open(os.path.join(path, out_filename + '.txt'), 'w') as out:
        for filename, out_list in results.items():
            out.write(filename + ' \n')
            out.writelines("%s\n" % l for l in out_list)
            out.write('\n\n')


#%% write xyz

def write_xyz(path, out_filename, results):
    with open(os.path.join(path, out_filename + '.xyz'), 'w') as out:
        for filename, out_list in results.items():
            out.writelines("%s\n" % l for l in out_list)
            out.write('\n\n')
    


#%% main function

def main(path, g09_files = None, out_filename = "SI_coords", 
         extension = '.log', out_type = 'both'):
    
    if not g09_files:
        g09_files = [x for x in os.listdir(path) if x.endswith(extension)]
    
    if len(g09_files) == 0:
        raise ValueError(f'No files of extension {extension} found.')
    
    for i, file in enumerate(g09_files):
        if not check_term(file, path):
            error_term(file, path)
            error_file = g09_files.pop(i)
            print(f'{error_file} did not end in normal termination.')
    
    
    if out_type == 'txt':
        results = {}
        for filename in g09_files:
            try:
                results[filename] = g09out_to_txt_list(path, filename)
                
            except Exception as e:
                print(f'Could not process {filename}. Error: {e}')
        
        write_txt(path, out_filename, results)
    
    elif out_type == 'xyz':
        results_xyz = {}
        for filename in g09_files:
            try:
                results_xyz[filename] = g09out_to_xyz(path, filename)
                
            except Exception as e:
                print(f'Could not process {filename}. Error: {e}')
        
        write_xyz(path, out_filename, results_xyz)
        
    elif out_type == 'both':
        results = {}
        results_xyz = {}
        for filename in g09_files:
            try:
                results[filename] = g09out_to_txt_list(path, filename)
                results_xyz[filename] = g09out_to_xyz(path, filename)
            except Exception as e:
                print(f'Could not process {filename}. Error: {e}')
        
        write_txt(path, out_filename, results)
        write_xyz(path, out_filename, results_xyz)
        
    
    


#%% input parser


if __name__ == '__main__':
    
    import argparse as ap
    parser = ap.ArgumentParser(prog = 'write_coordSI', 
                               description = """Write .txt file with information 
                               and coordinates from g09 output files 
                               in format for Supporting Information.""")
    
    parser.add_argument('-p', '--path', type = str, default = '.',
                        help = 'path for directory to work in')
    parser.add_argument('-i', '--input', type = list, default = None,
                        help = 'list of g09 output files. defaults to all files in working directory')
    parser.add_argument('-e', '--ext', type = str, default = '.log',
                        help = 'extension of g09 output files. if incorrect files wont be found')
    parser.add_argument('-o', '--out_name', type = str, default = 'SI_coords',
                        help = 'Name for output file (without extension), defaults to SI_coords')
    parser.add_argument('-ot', '--out_type', type = str, default = "both",
                        help = 'type of output for SI coordinates (txt/xyz/both)')
 
    args = parser.parse_args()
     
    main(args.path, g09_files = args.input, out_filename = args.out_name,
         extension = args.ext, out_type = args.out_type)
