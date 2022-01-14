#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  6 13:48:56 2021

@author: nat
"""

#molecule.py

"""Definition of molecule classes
for implementation in compchemtools scripts."""

#%% periodic table

periodic_table = ["","H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg",
                  "Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn",
                  "Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb",
                  "Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In",
                  "Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm",
                  "Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta",
                  "W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At",
                  "Rn","Fr","Ra","Ac","Th","Pa","U","Np","Pu","Am","Cm","Bk",
                  "Cf","Es","Fm","Md","No","Lr","Rf","Db","Sg","Bh","Hs","Mt",
                  "Ds","Rg","Uub","Uut","Uuq","Uup","Uuh","Uus","Uuo"]

#%% class Molecule

class Molecule():
    """Molecule object defined by atom types 
    (as dictionary of atom number: atom types)
    and coordinates (as dictionary of atom number: xyz coords (as np.array))
    and with attributes obtained from different computational jobs.
    These attributes have default values which can be reassigned.
    energy = 0, found = 0, charge = 0, mult = 1 (multiplicity).
    
    """
    
    # Should add function to check if coordinates and atom_types have the
    # same length
    def __init__(self, coordinates, atom_types):
        """coordinates and atom_types define the molecule and must have the 
        same length. Atom number in coordinates must correspond to the same 
        atom number in atom_types.
        """
        
        if len(coordinates) != len(atom_types):
            raise ValueError("coordinates and atom_types must have the same \
                             number of atoms (length).")
        else:                     
            self.coordinates = coordinates
            self.atom_types = atom_types
            self.energy = 0
            self.found = 0
            self.charge = 0
            self.mult = 1
            self.natoms = len(self.coordinates)
            self.title = 'NAME'
    
        
    def __repr__(self):
        return f'''Molecule with {self.natoms} atoms.
    {self.coordinates} '''

    def __str__(self):
        fullXYZstring = ('\n').join(self.strXYZ())
        return f'''Molecule {self.title} with {self.natoms} atoms. 
{fullXYZstring}'''

    def arrXYZ(self):
        """Returns a list of XYZ coordinates as np.arrays."""
        
        return [self.coordinates[atom] for atom in self.coordinates]
    
    def strXYZ(self):
        """Returns a list of strings with atom type and XYZ coordinates."""
        XYZ = self.arrXYZ()
        return [f'{self.atom_types[n]}  {XYZ[n-1][0]:.8f} {XYZ[n-1][1]:.8f} {XYZ[n-1][2]:.8f}'  \
                for n in self.atom_types]
    
    def csvXYZ(self):
        """Returns a list of strings with atom type and XYZ coordinates 
        separated by commas."""
        XYZ = self.arrXYZ()
        return [f'{periodic_table[self.atom_types[n]]}, {XYZ[n-1][0]:.8f}, {XYZ[n-1][1]:.8f}, {XYZ[n-1][2]:.8f}'  \
                for n in self.atom_types]        




        