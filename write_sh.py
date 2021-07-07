#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:25:52 2021

@author: nat
"""

#write_sh.py

""" Functions for writing .sh script files for running g09 jobs in HPC cluster 
with SGE. """

#%% modules

import os

#%% get_nproc function

def get_nproc(g09in_file):
    """Read g09 input file and extract number of processors used in job."""
    
    with open(g09in_file, 'r') as f:
        for line in f:
            if line.startswith('%n'):
                nproc = line.split('=')[1]
                break
    return nproc


#%% write_sh function

def write_sh(filename, nproc, time, jobname, g09in_file):
    """ Writes .sh file.
    filename includes path.
    nproc: number of processors requested.
    time: wall clock time, max 3 days. format HH:MM:SS, string.
    g09in_file: name of g09 input file to run job on cluster."""
    
    sge_chunk = ['#!/bin/bash', '#$ -S /bin/bash', '#',  
                 '### Job Name', f'#$ -N {jobname}', '#',
                 '# Setea HH:MM:SS tiempo de wall clock time, maximo 3 dias', 
                 f'#$ -l h_rt={time}', '#',
                 '### write out files in current directory', '#$ -cwd', '#',
                 "### Merge '-j y' (do not merge '-j n') stderr into stdout stream:",
                 '#$ -j y', '#', '### Number of procs requested', f'#$ -pe openmp {nproc}']

    gaussroot_chunk = ['# ------- Defining root directory for gaussian \n',
                       'g09root=/share/apps/Gaussian09/EM64T.SSE4.2-enabled',
                       'GAUSS_SCRDIR=/tmp',
                       'export g09root GAUSS_SCRDIR',
                       '. $g09root/g09/bsd/g09.profile']
    
    stdout_chunk = ['# -------- SECTION print some infos to stdout --------------------------------- \n',
                    'echo " "',
                    '''echo "START_TIME           = `date +'%y-%m-%d %H:%M:%S %s'`"''',
                    '''START_TIME=`date +%s`''',
                    '''echo "HOSTNAME             = $HOSTNAME"''',
                    '''echo "JOB_NAME             = $JOB_NAME"''',
                    '''echo "JOB_ID               = $JOB_ID"''',
                    '''echo "SGE_O_WORKDIR        = $SGE_O_WORKDIR"''',
                    '''echo "NSLOTS               = $NSLOTS"''',
                    '''echo " "''']
    
    exec_chunk = ['# -------- SECTION executing program --------------------------------- \n',
                  'echo " "',
                  'echo "Running:"',
                  'echo " " \n',
                  f'g09 {g09in_file}']
    
    cleanup_chunk = ['# -------- SECTION final cleanup and timing statistics ------------------------ \n',
                     '''echo "END_TIME (success)   = `date +'%y-%m-%d %H:%M:%S %s'`"''',
                     '''END_TIME=`date +%s`''',
                     '''echo "RUN_TIME (hours)     = "`echo "$START_TIME $END_TIME" | awk '{printf("%.4f",($2-$1)/60.0/60.0)}'` \n''',
                     'exit 0']
    
    with open(filename, 'w') as f:
        f.write('\n'.join(sge_chunk))
        f.write('\n\n\n')
        f.write('\n'.join(gaussroot_chunk))
        f.write('\n\n\n')
        f.write('\n'.join(stdout_chunk))
        f.write('\n\n\n')
        f.write('\n'.join(exec_chunk))
        f.write('\n\n\n')
        f.write('\n'.join(cleanup_chunk))
        f.write('\n\n\n')

#%% main function

def main(path, time, g09_files = None, sh_name = 'a', extension = '.com'):
    """Writes .sh for list of g09 files.
    If no list is provided, g09 files are looked for in path and all found
    are used.
    """
    
    if not g09_files:
        g09_files = [x for x in os.listdir(path) if x.endswith(extension)]
    
    if len(g09_files) == 0:
        print('No g09 input files found.')
        
    for i, file in enumerate(g09_files):
        nproc = get_nproc(os.path.join(path, file))
        jobname = file.split('.')[0]
        write_sh(os.path.join(path, sh_name + str(i+1) + '.sh'), 
                 nproc, time, jobname, file)
        
        
#%% 

if __name__ == '__main__':
    
    import argparse as ap
    parser = ap.ArgumentParser(prog = 'write_sh', 
                               description = 'Write .sh script files from g09 input files')
    
    parser.add_argument('-p', '--path', type = str, default = '.',
                        help = 'path for directory to work in')
    parser.add_argument('-i', '--input', type = list, default = None,
                        help = 'list of g09 input files. defaults to all files in working directory')
    parser.add_argument('-sn', '--sh_name', type = str, default = 'a',
                        help = 'name for sh files')
    parser.add_argument('-t', '--time', type = str, default = '11:59:59',
                        help = 'wall clock time for job, format HH:MM:SS')
    parser.add_argument('-e', '--ext', type = str, default = '.com',
                        help = 'extension of g09 input files. if incorrect files wont be found')

    args = parser.parse_args()
     
    main(args.path, args.time, g09_files = args.input, sh_name = args.sh_name,
         extension = args.ext)

       
        
        
        
    

            