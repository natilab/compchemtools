#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 17:27:50 2021

@author: nat
"""

# compchemtools.py

"""Interactive wrapper for computational chemistry scripts."""

#%% modules



#%% function to get task

def get_task():
    """Gets task number (int) from command line input."""
    
    print(f'''Tasks:
          1: Process g09 outputs (opt, freq or sp jobs).
          2: Write .sh files for g09 input files.
          3: Process conformational search results (.hcs).
          4: Change link0 and route lines in existing g09 input files.''')
    task_num = int(input("Enter task number:"))
    
    return task_num


#%% functions to get additional arguments according to task

def get_args_1():
    """Get arguments for task 1 from command line input."""
    
    # task 1: Process g09 outputs. Arguments needed for proc_g09out.py
    
    path = input("Path to g09 output files:")
    extension = input("Extension of g09 output files (.log/.out):")
    sp = input("Only single point calculation? (y/n):")
    
    if sp == 'n':
        get_sp = False
    else:
        get_sp = True
    
    return path, extension, get_sp


def get_args_2():
    """Get arguments for task 2 from command line input."""
    
    # task 2: write .sh files. Arguments needed for write_sh.py
    
    path = input("Path to g09 input files:")
    extension = input("Extension of g09 output files (.com/.gjf):")
    time = input('Wall clock time for job, format HH:MM:SS:')
    nfiles = int(input('Number of g09 inputs in each sh \
                       (all must have same nproc):'))
    
    return path, extension, time, nfiles


def get_args_3():
    """Get arguments for task 3 from command line input."""

    # task 3: Process .HCS file and write g09 input files. 
    # Arguments needed for hcs_to_g09.py
    
    path = input("Path to conformational search (.hcs) files:")
    extension = input("Extension of g09 output files (.com/.gjf):")
    
    mp = input('Default molecular properties? (y/n):')
    mps = []
    
    if mp == 'n':
        charge = int(input("Molecule charge:"))
        mult = int(input("Molecule multiplicity:"))
        mps = mps + [charge, mult]
    
    gj = input('Default g09 job input? (y/n):')
    gjs = []
    
    if gj == 'n':
        nproc = int(input("Number of processors (nproc):"))
        mem = int(input("Memory to use (in GB, only write number):"))
        func = int(input("Functional:"))
        bset = int(input("Basis set:"))
        job = input("G09 job keywords and options as would appear in input file:")
        gjs = gjs + [nproc, mem, func, bset, job]
    
    return path, extension, mps, gjs
    


def get_args_4():
    """Get arguments for task 4 from command line input."""
    
    # task 4: rewrite g09 files. Arguments needed for rw_g09in.py
    path = input("Path to g09 input files:")
    extension = input("Extension of g09 output files (.com/.gjf):")
    nproc = int(input("Number of processors to use (nproc):"))
    mem = int(input("Memory to use (in GB, only write number):"))
    route = input("Route line for input (without # symbol):")
    chk = input("Add chk line to input files? (y/n):")
    
    if chk == 'n':
        chk = False
    else:
        chk = True
    
    return path, extension, nproc, mem, route, chk

#%% task 1 

def task1():
    """Get arguments for task 1 and do task."""
    import proc_g09out
    
    path, extension, get_sp = get_args_1()
    
    proc_g09out.main(path, extension = extension, get_sp = get_sp)

#%% task 2 

def task2():
    """Get arguments for task 2 and do task."""
    import write_sh
    
    path, extension, time, nfiles = get_args_2()
    
    write_sh.main(path, time, extension = extension, n_files = nfiles)
    
    
#%% task 3 

def task3():
    """Get arguments for task 3 and do task."""
    import hcs_to_g09
    
    path, extension, mps, gjs = get_args_3()
    
    if mps:
        charge = mps[0]
        mult = mps[1]
    else:
        charge = 0
        mult = 1
    
    if gjs:
        nproc = gjs[0]
        mem = gjs[1]
        func = gjs[2]
        bset = gjs[3]
        job = gjs[4]
    else:
        nproc = 4
        mem = 1
        func = 'B3LYP'
        bset = '6-31G*'
        job = ''
        
    
    hcs_to_g09.main(charge = charge, multiplicity = mult, nproc = nproc, 
                    mem = mem, func = func, basis = bset, job = job,
                    extension = extension, pathin = path)


#%% task 4 

def task4():
    """Get arguments for task 4 and do task."""
    import rw_g09in
    
    path, extension, nproc, mem, route, chk = get_args_4()
    
    rw_g09in.main(path, extension = extension, route = route, chk = chk, 
                  mem = mem, nproc = nproc)
