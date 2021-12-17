#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  5 14:24:48 2021

@author: nat
"""

"""Set of functions for writing g09 input files from molecular geometry and
job and route section details."""


#%% modules

from cctools.molecule import Molecule


#%% define class for g09 input

class g09_job(Molecule):
    """Object with molecule geometry and specifications and 
    all information necessary for creating g09 input.
    """
    
    def __init__(self, molecule, nproc = 4, mem = 2, func = '', 
                 basis = '', job = '', chk = None):
        super().__init__(molecule.coordinates, molecule.atom_types)
        self.charge = molecule.charge
        self.mult = molecule.mult # multiplicity
        self.nproc = nproc #number of processors used
        self.mem = mem # maximum memory
        self.chk = chk # chk name, if none, line is not written in out
        self.func = func # functional
        self.basis = basis # basis set
        self.job = job # job keywords and options as string
        self.comment = None
        self.additional = False # for now the True option is not written
    
    def get_link0(self):
        """Returns lines for link0 command section of g09 input as a list"""
        
        link0 = [f'%nprocshared={self.nproc}',
                 f'%Mem={self.mem}GB']
        
        if self.chk:
            link0.insert(0, f'%chk={self.chk}')
        
        return link0
    
    def get_route(self):  
        """Return route section line for g09 input as string"""
        
        return f'# {self.func}/{self.basis} {self.job}'
    
    def get_specs(self):
        """Returns string with line for initial molecule specifications 
        (charge and multiplicity).
        """
        
        return f'{self.charge}  {self.mult}'
    
    # def get_coords(self):
    #     """Returns list of strings for cartesian coordinates needed in
    #     g09 input. Each element would be a line in the input file."""
        
    #     return [f'{self.atom_types[atom]}  {self.coordinates[atom].x}  {self.coordinates[atom].y}  {self.coordinates[atom].z}' 
    #             for atom in self.atom_types]
    
    def write_input(self, file_name):
        """Writes input file into provided filename with g09 input format
        using Cartesian Coordinates. Encoding: ASCII"""
        
        blank = '\n\n'
        
        with open(file_name, 'w', encoding = 'ascii') as out:
            
            # Write link0 command lines, turn list from getlin0 into lines
            out.writelines("%s\n" % l for l in self.get_link0()) 
            out.write('\n')
            
            # Write route section, as returned from get_route
            out.write(self.get_route())
            out.write(blank)
            
            # Write comment line
            if self.comment:
                out.write(self.comment)
            else:
                out.write('comment line')
            out.write(blank)
            
            # Write Molecule Specifications
            out.write(self.get_specs())
            out.write('\n')
            
            #   atomic coordinates
            out.writelines("%s\n" % l for l in self.strXYZ())
            
            # Final blank lines
            out.write('\n\n')
    
    
    
    
        
    

