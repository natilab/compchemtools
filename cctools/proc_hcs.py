#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:03:46 2021

@author: nat
"""

#proc_hcs.py

"""Set of functions for the extraction of useful information as well as geometries
for all found conformations in a conformational search performed with Hyperchem,
by the processing of .HCS file."""


#%% modules

from cctools.molecule import Molecule

import numpy as np

#%% hcs_parser

def parse_hcs(hcs_file):
    """Reads and processes hcs_file. 
    Input: .hcs file, conformational search output from HyperChem program.
    Out: list of lists with lines for each conformer. Lines contain
    conformer info (energy, found) and coordinates.    
    First element of list: initial info from conf search.
    """
    Confs = []
    CurrentConf = []
    
    try:
        with open(hcs_file, 'rt') as hcs:
            for line in hcs:
                if 'Conform' in line and CurrentConf:
                    Confs.append(CurrentConf[:])
                    CurrentConf = []
                CurrentConf.append(line)
            Confs.append(CurrentConf)
    
    except Exception:
        print('Error: Cannot find file')
    
    return Confs


#%%  Functions to extract conformation info and coords

def get_conf_data(conformer):
    """In: conformer is a list of strings (lines) with the info for 1 conformer.
    Out: tuple with energy, found values for the conformer."""
    
    for line in conformer:
        if 'Energy' in line:
            energy = float(line.split('=')[1])
        if 'Found' in line:
            found = float(line.split('=')[1])
    
    return energy, found

def get_conf_coord(conformer):
    """In: conformer is a list of strings (lines) with the info for 1 conformer.
    Out: dictionary with atom number as key and cartesian coordinates 
    as value.
    """
    
    conf_XYZ = {}
    
    for line in conformer:
        if line.startswith('X'):
            atom = line[2:].split(')=')
            atom_num = int(atom[0])
            rawXYZ = atom[1].split()
            
            conf_XYZ[atom_num] = np.array([float(coord) for coord in rawXYZ])

    return conf_XYZ
    
    
    
def get_atom_types(init_info):
    """In: list with lines from initial information of hcs file 
    (conf search).
    Out: dictionary with atom number as key and atom type as value.
    """
    
    atom_types = {}
    for line in init_info:
        if line.startswith('atom'):
            atom = line[4:].split()
            atom_num = int(atom[0])
            atom_type = atom[2]
            
            atom_types[atom_num] = atom_type
    
    return atom_types
            


#%% function to extract conformations from parsed hcs file

def extract_confs(confs_list, charge = 0, multiplicity = 1):
    """In: list of lists with lines from hcs file (output from parse_hcs).
    Out: List of Molecule objects. 
    Each molecule contains energy, found, cartesian coordinates 
    and atom types for the corresponding coformer. 
    Charge and multiplicity different than 0, 1 can be provided.
    """
    
    atom_types = get_atom_types(confs_list.pop(0)) 
    # dictionary atom_number : atom_type
    
    conformers = []
    for conformer in confs_list:
        energy, found = get_conf_data(conformer)
        coords_dict = get_conf_coord(conformer)
        
        molecule = Molecule(coords_dict, atom_types)
        molecule.energy = energy
        molecule.found = found
        molecule.charge = charge
        molecule.mult = multiplicity
        
        conformers.append(molecule)
    
    return conformers


#%% main function

def main(hcs_file, charge = 0, multiplicity = 1):
    """Processes hcs_file into a list of molecule objects for 
    each found conformation or conformer.
    """
    
    confs_list = parse_hcs(hcs_file)
    
    return extract_confs(confs_list, charge, multiplicity)


            
        
        
    
    
    

