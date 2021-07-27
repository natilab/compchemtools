#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 12:21:48 2021

@author: nat
"""

#g09freq.py

"""Extract information of interest from g09 frequency job."""

#%% modules

from g09opt import get_SCF

#%% get frequencies 

def get_freq(freq_job):
    """From parsed g09 frequency job, get first 3 frequencies. 
    Return list with 3 values (ordered)."""
    
    for line in freq_job:
        if line.strip().startswith('Frequencies'):
            rawFreq = line.split('--')[1]
            freqs = [float(freq) for freq in rawFreq.split()]
            break
    
    return freqs

def get_Nneg(freqs):
    """returns number of negative frequencies from freq list."""
    
    n = 0
    for freq in freqs:
        if freq < 0:
            n += 1
    
    return n
    
def freq_analysis(freq_job):
    """From parsed g09 frequency job, analyses frequencies and returns
    n: number of negative frequencies,
    value: value of negative frequency (if n = 1)"""
    freqs = get_freq(freq_job)
    n = get_Nneg(freqs)
    
    if n == 1:
        return n, freqs[0]
    
    else:
        return n
    

#%% get energies

def get_energies(freq_job):
    """In: parsed g09 frequency job.
    Out: list of enegies:
        SCF energy
        Sum of electronic and ZPE
        Sum of electronic and thermal energies
        Sum of electronic and thermal enthalpies
        Sum of electronic and thermal free energies.
    All energies in hartress.
    """
    
    SCF = get_SCF(freq_job)
    energies = [SCF]
    
    for line in freq_job:
        if 'Sum of electronic' in line:
            sum_energy = float(line.split('=')[1])
            energies.append(sum_energy)
            
    return energies


#%% full freq processing

def main(freq_job):
    """Processes parsed g09 freq job and returns
    ((number of neg frequencies, value of neg frequency (if n ==1)), list of energies)"""
    
    return freq_analysis(freq_job), get_energies(freq_job)