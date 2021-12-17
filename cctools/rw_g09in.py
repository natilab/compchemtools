#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 20:47:57 2021

@author: nat
"""

#rewrite_g09in.py

"""Script for re-writing a g09 input file: from a g09 input file, replace lines 
with desired Link specs and route line.
"""

#%% modules

import os

#%% 


def rewrite_g09in(g09in_file, route = None, chk = None, mem = None, nproc = None):
    with open(g09in_file, 'r') as file:
        in_file = file.read().splitlines()
    
    
    with open(g09in_file, 'w') as newfile:
        i = 0
        if chk:
            newfile.write(f'%chk={chk} \n')
            
            if 'chk' in in_file[0]:
                i += 1
        
        while i < len(in_file):
            line = in_file[i]
            i += 1
            if nproc and 'nproc' in line:
                newfile.write(f'%nprocshared={nproc} \n')
            elif mem and 'Mem' in line:
                newfile.write(f'%Mem={mem}GB \n')
            elif route and line.startswith('#'):
                newfile.write(f'# {route} \n')
            else:
                newfile.write(f'{line} \n')
                
#%% 
                
def main(path, g09_files = None, extension = '.com', route = None, chk = False, mem = None, nproc = None):

    if not g09_files:
        g09_files = [x for x in os.listdir(path) if x.endswith(extension)]
    
    if len(g09_files) == 0:
        print('No g09 input files found.')    
    
    if chk == 'F':
        chk = False

    for file in g09_files:
        if chk: 
            chk = file[:-4]+'.chk'
            rewrite_g09in(os.path.join(path, file), route = route, chk = chk, mem = mem, nproc = nproc)
        if not chk:
            rewrite_g09in(os.path.join(path, file), route = route, mem = mem, nproc = nproc)
            

#%% 

if __name__ == '__main__':
    
    import argparse as ap
    parser = ap.ArgumentParser(prog = 'rewrite_g09', 
                               description = 'Re-write g09 input files with provided link0 and route specs.')
    
    parser.add_argument('-p', '--path', type = str, default = '.',
                        help = 'path for directory to work in')
    parser.add_argument('-i', '--input', type = list, default = None,
                        help = 'list of g09 input files. defaults to all files in working directory')
    parser.add_argument('-r', '--route', type = str, default = None,
                        help = 'route line for input (without # symbol)')
    parser.add_argument('-m', '--mem', type = int, default = None,
                        help = 'memory for input (in GB)')
    parser.add_argument('-np', '--nproc', type = int, default = None,
                        help = 'nprocshared for input')
    parser.add_argument('-c', '--chk', type = bool, default = False,
                        help = 'add chk line to input files (T/F)')
    parser.add_argument('-e', '--ext', type = str, default = '.com',
                        help = 'extension of g09 input files. if incorrect files wont be found')

    args = parser.parse_args()
     
    main(args.path, g09_files = args.input, extension = args.ext, route = args.route,
         chk = args.chk, mem = args.mem, nproc = args.nproc)

