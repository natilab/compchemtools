#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 13:48:56 2021

@author: nat
"""

#molecule.py

"""Definition of molecule classes
for implementation in compchemtools scripts."""

#%% class coordinate

class Coordinate():
    """Cartesian coordinate in 3D space."""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def __repr__(self):
        return f'Coordinate({self.x}, {self.y}, {self.z})'
    
    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'

#%% class Molecule

class Molecule():
    """Molecule object defined by atom types 
    (as dictionary of atom number: atom types)
    and coordinates (as dictionary of atom number: Coordinates)
    and with attributes obtained from different computational jobs.
    These attributes have default values which can be reassigned.
    energy = 0, found = 0, charge = 0, mult = 1 (multiplicity).
    """
    
    # Should add function to check if coordinates and atom_types have the
    # same length
    def __init__(self, coordinates, atom_types):
        self.coordinates = coordinates
        self.atom_types = atom_types
        self.energy = 0
        self.found = 0
        self.charge = 0
        self.mult = 1
        self.natoms = len(self.coordinates)
    
    def __repr__(self):
        return f'''Molecule with {self.natoms} atoms.
    {self.coordinates}'''
        




        