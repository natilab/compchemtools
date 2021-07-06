#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:03:46 2021

@author: nat
"""

#%% modules

# import os as os
# import re as re
#import pandas as pd
#import numpy as np
#import argparse as ap
#import sys

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
        # InitInfo = Confs[0]
        # del Confs[0]
    
    except Exception as exc:
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
    Out: dictionary with atom number as key and coordinates [x, y, z] as value.
    """
    
    conf_coord = {}
    
    for line in conformer:
        if line.startswith('X'):
            atom = line[2:].split(')=')
            atom_num = int(atom[0])
            coords = atom[1].split()
            
            conf_coord[atom_num] = [float(coord) for coord in coords]

    return conf_coord
    
    
    
def get_atom_types(init_info):
    """In: list with lines from initial information of hcs file 
    (conf search).
    Out: dictionary with atom number as key and atom type as value.
    """
    
    atom_types = {}
    for line in init_info:
        if line.startswith('atom'):
            atom = line[4:].split('**')[0]
            atom_num = atom.split('-')[0].strip(' ')
            atom_type = atom.split('-')[1].strip(' ')
            
            atom_types[atom_num] = atom_type
    
    return atom_types
            


#%% function to extract conformations from parsed hcs file

def extract_confs(confs_list):
    """In: list of lists with lines from hcs file (output from parse_hcs).
    Out: Dictionary with conformer number as key and list of 
    [energy, found, coords] as value. Coords is a list of lists as 
    [atom number, atom type, (x, y, z)].
    """
    
    atom_types = get_atom_types(confs_list.pop(0)) # dictionary atom_number : atom_type
    
    conformers = {}
    for i, conformer in enumerate(confs_list):
        energy, found = get_conf_data(conformer)
        coords_dict = get_conf_coord(conformer)
        coords_list = []
        for atom in coords_dict:
            coords_list.append([atom_types[atom], atom,
                                tuple(coords_dict[atom])])
        conformers[i] = [energy, found, coords_list]
    
    return conformers


#%% main function

def main(hcs_file):
    """Processes hcs_file into a dictionary with the information for 
    each found conformer.
    """
    
    confs_list = parse_hcs(hcs_file)
    
    return extract_confs(confs_list)


            
        
        
    
    
    

