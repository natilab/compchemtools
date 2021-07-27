#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 15:10:12 2021

@author: nat
"""

#g09opt.py

"""Extract information of interest from g09 optimisation job."""

#%%

import numpy as np
# import re

from molecule import Molecule



#%% functions: split optimization chunk into opt steps and check opt 

def split_opt(g09opt):
    """Split parsed g09 optimization output lines into chunks where 
    each one has the information for an opt step. 
    Split is done at 'SCF Done' line.
    In: parsed g09 output file lines.
    Out: list of chunks, each chunk is a list of lines (strings).
    First chunk has all initial info and first opt step, 
    last chunk has lines between last 
    SCF energy and termination line.
    Length of list is number of opt steps + 1.
    """
    
    opt_steps = []
    current_step = []
    
    for line in g09opt:
        current_step.append(line)
        if 'SCF Done' in line:
            opt_steps.append(current_step[:])
            current_step = []
            
    opt_steps.append(current_step) # to add final chunk
    
    return opt_steps
        

def check_opt(opt_steps):
    """Check if 'Optimization completed' line is present in last chunk of
    opt_steps.
    If not, returns error."""
    
    completed = False
    
    for line in opt_steps[-1]:
        if 'Optimization completed' in line:
            completed = True
    
    if not completed:
        raise ValueError('Optimization completed not found: Error in optimization job or parsing file.')
    

#%% functions: get SCF energy/ies

def get_SCF(opt_step):
    """Get SCF Energy from the lines of an optimization step.
    In: list with chunk of lines for opt step.
    Out: energy (float) in hartrees.
    If energy is not found, returns 0.0"""
    
    SCFenergy = 0.0
    
    for line in reversed(opt_step):
        # walks through opt_step from last to first, to speed calc time
        # SCF Done should be last line
        if 'SCF Done' in line:
            SCFenergy = line.split()[4]
    
    return SCFenergy


def get_finalSCF(opt_steps):
    """Get SCF energy for the final geometry of a Gaussian 09 optimisation job.
    In: opt_steps list (chunks of lines with each opt step).
    Out: SCF energy as float."""
    
    return get_SCF(opt_steps[-2])


def get_allSCFs(opt_steps):    
    """Get SCF energy for all steps of a Gaussian 09 optimisation job.
    In: opt_steps list (chunks of lines with each opt step).
    Out: SCF energies as ordered np array."""
    
    SCFenergies = np.zeros(len(opt_steps)-1) # build an array with the amount of opt steps
    
    for i, step in enumerate(opt_steps):
        energy = get_SCF(step)
        SCFenergies[i] = energy
    
    return SCFenergies

#%% functions: get coordinates, build molecule

def get_raw_coords(opt_step):
    """Get coordinates for the geometry of the start of an optimization step.
    In: opt step chunk.
    Out: list of raw coordinates in g09 format."""

    raw_coords = []
    
    for i, line in enumerate(opt_step):
        if 'Standard orientation' in line:
            j = i+5
            coord = True
            while coord:
                line = opt_step[j]
                if '---' in line:
                    coord = False
                else:
                    raw_coords.append(line.strip('\n'))
                    j += 1
                    
            break
    
    return raw_coords

def raw_to_coord(raw_coords):
    """Convert raw g09 coordinate list into
    XYZ: dictionary with atom number as key 
    and cartesian coordinates (np array) as value,
    and types: dictionary with atom number as key and element number (atom
    type) as value.
    Out: XYZ, types
    """
    
    XYZ = {}
    types = {}
    for raw in raw_coords:
        coord_list = raw.split()
        atom = int(coord_list[0])
        XYZ[atom] = np.array([float(coord_list[3]),
                              float(coord_list[4]),
                              float(coord_list[5])])
        types[atom] = int(coord_list[1])
    
    return XYZ, types


def get_molecule(opt_step):
    """Get coordinates and atom types from opt_step and build a Molecule
    object."""
    
    raw = get_raw_coords(opt_step)
    coords, types = raw_to_coord(raw)
    
    molecule = Molecule(coords, types)
    
    return molecule
                
            
        

def get_finalMolecule(opt_steps):
    """In: list of opt_steps.
    Return Molecule object for final (optimized) geometry."""
    
    final_mol = get_molecule(opt_steps[-2])
    
    return final_mol

#%% get additional info

def get_specs(opt_steps):
    """In: list of opt_steps.
    Returns charge, multiplicity and name (filename). 
    """
    
    for line in opt_steps[0]:
        if 'Input' in line:
            name = line.split('=')[1][:-5]
        elif 'Charge' in line:
            charge = int(line.split()[2])
            mult = int(line.split()[5])
            break
    
    return charge, mult, name
            

#%% full processing of opt chunk

def main(g09opt, steps):
    """Input: list of strings with optimization output of g09 calculation.
    Out: finalSCF, finalMol, allSCF.
    finalSCF: optimized SCF energy (float, hartrees)
    finalMol: Molecule object for optimized geometry
    allSCF: np array with ordered SCF energies (if steps == True)."""
    
    opt_steps = split_opt(g09opt)
    check_opt(opt_steps)
    
    charge, mult, name = get_specs(opt_steps)
    finalSCF = get_finalSCF(opt_steps)
    
    finalMol = get_finalMolecule(opt_steps)
    finalMol.charge = charge
    finalMol.mult = mult
    finalMol.title = name
    finalMol.energy = finalSCF
    
    if steps == True:
        allSCF = get_allSCFs(opt_steps)
        return finalSCF, finalMol, allSCF
    
    else:
        return finalSCF, finalMol
    


#%% read opt
# import os



# def remove_empty(string):
#     """Returns string without empty lines"""
    
#     return "".join([s for s in string.strip().splitlines(True) if s.strip("\r\n").strip()])

# opt_chunk = []
# with open('5Xa.log', 'r') as out:
# #    out = remove_empty(out)
#     for i, line in enumerate(out):
#         opt_chunk.append(line)
#         if 'Normal termination' in line:
#             print(line)
#             break
            
    


    