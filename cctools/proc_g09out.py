#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:26:03 2021

@author: nat
"""
#proc_g09out.py

#%% modules

import os

from cctools import g09opt, g09freq
# from molecule import Molecule
from cctools.write_g09in import g09_job

#%% open file and check normal term

# Function to read
# last N lines of the file
def LastNlines(fname, N):
    """Reads last N lines of a files. Return list with the last N lines."""
     
    # assert statement check
    # a condition
    assert N >= 0
     
    # declaring variable to implement exponential search
    pos = N + 1
     
    # list to store last N lines
    lines = []
     
    with open(fname) as f:
         
        # loop which runs until size of list becomes equal to N
        while len(lines) <= N:
             
            try:
                # moving cursor from left side to pos line from end
                f.seek(-pos, 2)
         
            # exception block to handle any run time error
            except IOError:
                f.seek(0)
                break
             
            # finally block
            # add lines to list after each iteration
            finally:
                lines = list(f)
             
            # increasing value of variable exponentially
            pos *= 2
             
    return lines[-N:]


def check_term(g09out_name, path):
    """Returns True if normal termination line is found at the end of file,
    False otherwise.
    """
    file = os.path.join(path, g09out_name)
    final_lines = LastNlines(file, 3)

    normal_term = False
        
    for line in reversed(final_lines):
        if 'Normal termination' in line:
            normal_term = True
            break
        
    return normal_term

def error_term(g09out_name, path):
    """Task to follow if file doesn't end in normal termination
    (move file to subfolder called 'not_normal_term'."""
    
    destination_path = os.path.join(path, 'not_normal_term')
    try:
        os.mkdir(destination_path)
    except FileExistsError:
        pass
    
    os.rename(os.path.join(path, g09out_name), os.path.join(destination_path, g09out_name))

    
#%% get jobs

def get_jobs(g09out):
    """Find what jobs were done from the g09 output file.
    return string of jobs (separated by whitespaces) and route line.
    """
    
    jobs = 'sp '
    with open(g09out) as out:
        for line in out:
            if line.strip().startswith('#'):
                route = line.strip('\n').strip(' ')
                line = next(out)
                while not line.strip().startswith('-'):
                    route += line.strip('\n').strip(' ')
                    line = next(out)
                break
            
    if 'opt' in route.lower():
        jobs += 'opt '
    if 'freq' in route.lower():
        jobs += 'freq '
    if 'irc' in route.lower():
        jobs += 'irc '
    if 'stable' in route.lower():
        jobs += 'stable '
            
    return jobs, route
                
def parse_file(g09out, jobs):
    """Function to parse file into list of strings.
    According to amount of jobs, it splits it at normal termination line"""
    
    parsed_out = []
    
    if len(jobs.split()) > 2:
        job_chunk = []
        with open(g09out, 'r') as out:
            for line in out:
                job_chunk.append(line)
                if 'Normal termination' in line:
                    parsed_out.append(job_chunk)
                    job_chunk = []
    else:
        with open(g09out, 'r') as out:
            for line in out:
                parsed_out.append(line)
                
                
    return parsed_out
        
        
#%% jobs processing

# A function is defined for the processing of each type of jobs

def opt_proc(parsed_opt, steps):
    """Does processing for parsed optimization job.
    If steps = False, returns only final SCF energy.
    If steps = True, return also np array with energy for each step."""
    
    return g09opt.main(parsed_opt, steps)
    
def freq_proc(parsed_freq):
    """Does processing for parsed optimization job."""
    
    return g09freq.main(parsed_freq)



#%% combination of processing functions

def out_proc(g09out_name, pathin, steps, get_sp = False):
    """Processes output according to jobs found in it. 
    If opt was done, g09 input files with optimized geoms are written in 'geometries' subfolder.
    Out: result_headers list and results list (with values corresponding to headers).
    """
    
    jobs, route = get_jobs(os.path.join(pathin, g09out_name))
    parsed_out = parse_file(os.path.join(pathin, g09out_name), jobs)
    
    
#    result_headers = ['filename', 'route', 'jobs']
    results = [g09out_name, f'"{route}"' , jobs]
    
    if 'opt' in jobs:
        try:
            os.mkdir(os.path.join(pathin, 'geometries'))
        except FileExistsError:
            pass            
        pathout = os.path.join(pathin, 'geometries')
        
        if 'freq' in jobs:
            # result_headers += ['n_negFreq', 'neg_freq', 'SCFenergy', 'electronic+ZPE',
            #                   'electronic+enthalpy', 'electronic+entropy', 'electronic+free']

            # Process opt+freq calc
            
            opt_results = opt_proc(parsed_out[0], steps)
            
            #For now, only process finalSCF and final geometry.
            
            ### write g09 input with final geom
            input_name = g09out_name.rsplit(".", 1)[0] + '_geom.com'
            g09_in = g09_job(opt_results[1]) 
            g09_in.write_input(os.path.join(pathout, input_name))
            
            ### Process freq (also gets SCF)
            
            freqs, energies = freq_proc(parsed_out[1])
            
            if type(freqs) != int:
                results += [freqs[0], freqs[1]] + energies
            else:
                results += [freqs, 'NA'] + energies
            
        
        else:
            # only opt calc 
            # to incorporate other combinations, extend later

            # result_headers += ['SCFenergy']

            opt_results = opt_proc(parsed_out, steps)
            
            #For now, only process finalSCF and final geometry.
            
            ### write g09 input with final geom
            input_name = g09out_name.rsplit(".", 1)[0] + '_opt.com'
            g09_in = g09_job(opt_results[1]) 
            g09_in.write_input(os.path.join(pathout, input_name))
           
            results.append(opt_results[0])
            
    
    elif 'freq' in jobs:
        # process only freq calc
        # result_headers += ['n_negFreq', 'neg_freq', 'SCFenergy', 'electronic+ZPE',
        #                   'electronic+enthalpy', 'electronic+entropy', 'electronic+free']
        
        freqs, energies = freq_proc(parsed_out)
                    
        if type(freqs) != int:
            results += [freqs[0], freqs[1]] + energies
        else:
            results += [freqs, 'NA'] + energies
    
        
    elif get_sp:
        # analyse single point, get SCF energy
        results.append(g09opt.get_SCF(parsed_out))
            
    else:
        raise ValueError('The type of calculation cannot be processed yet.')

    return results

#%% main function

def main(path, g09_files = None, steps = False, extension = '.log', get_sp = False):
    """Processes g09 output files. 
    If no list of files is provided, g09 out files ar looked for in path and
    all found are used.
    All files must have done the same calculation.
    """
    if not g09_files:
        g09_files = [x for x in os.listdir(path) if x.endswith(extension)]
    
    if len(g09_files) == 0:
        raise ValueError(f'No files of extension {extension} found.')
    
    for i, file in enumerate(g09_files):
        if not check_term(file, path):
            error_term(file, path)
            error_file = g09_files.pop(i)
            print(f'{error_file} did not end in normal termination.')
            
    jobs = get_jobs(os.path.join(path, g09_files[0]))[0]

    if 'freq' in jobs:
        result_headers = ['filename', 'route', 'jobs', 'n_negFreq', 'neg_freq', 'SCFenergy', 
                          'electronic+ZPE', 'electronic+enthalpy', 'electronic+entropy', 'electronic+free']
    else: # opt or SP jobs, no freq
        result_headers = ['filename', 'route', 'jobs', 'SCFenergy']
    
    results = []
    for filename in g09_files:
        try:
            results.append(out_proc(filename, path, steps, get_sp))
        except Exception as e:
            print(f'Could not process {filename}. Error: {e}')
    
    with open(os.path.join(path, 'g09_results.csv'), 'w') as out:
        out.write(','.join(result_headers))
        out.write('\n')
        for line in results:
            out.write(','.join([str(x) for x in line]))
            out.write('\n')
        
#%% input parser


if __name__ == '__main__':
    
    import argparse as ap
    parser = ap.ArgumentParser(prog = 'proc_g09out', 
                               description = 'Process g09 output files with opt, freq or SP jobs.')
    
    parser.add_argument('-p', '--path', type = str, default = '.',
                        help = 'path for directory to work in')
    parser.add_argument('-i', '--input', type = list, default = None,
                        help = 'list of g09 output files. defaults to all files in working directory')
    parser.add_argument('-e', '--ext', type = str, default = '.log',
                        help = 'extension of g09 output files. if incorrect files wont be found')
    parser.add_argument('-sp', '--get_sp', type = bool, default = False,
                        help = 'get SCF energy from SP or other calculations')
    parser.add_argument('-s', '--steps', type = bool, default = False,
                        help = 'if opt job was done, get array of SCF energy por each opt step. Not implemented yet.')
 
    args = parser.parse_args()
     
    main(args.path, g09_files = args.input, steps = args.steps,
         extension = args.ext, get_sp = args.get_sp)