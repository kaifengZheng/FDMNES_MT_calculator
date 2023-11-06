import numpy as np
import glob
import os
import shutil
import subprocess
import random
import string
import numpy as np
import time,datetime
import json
import argparse
from pymatgen.core import Element
from glob import glob
import sys
import toml
from tqdm import tqdm




        
#inputs = sys.argv     


#ncores  = int(inputs[1])
#ind   = int(inputs[2])


#print(ind)
config = toml.load('config.toml')

def write_FDMNESinp(template_dir,pos_filename,CA,site=None):
    """
    xyz
    """
    atomic_num=Element(CA).Z
    with open(template_dir) as f:
        template = f.readlines()
    title=pos_filename.split('.')[0].split('/')[-1]
    atoms,coords=read_xyz(pos_filename)

    with open(f"FDMNESinp//{title}.inp",'w') as f:
        f.write(f"TITLE {title}\n")
        f.writelines(template)
        f.write('\n\n')
        if site == None:
            f.write("Z_absorber")
            f.write(f"{atomic_num}\n\n")
        else:
            f.write("absorber")
            f.write(f"{site}\n\n")
        f.write('Molecule')
        f.write("1   1   1   90   90   90")
        for i in range(len(atoms)):
            f.write(f"{Element(atoms[i]).Z} {coords[i][0]} {coords[i][1]} {coords[i][2]}")
        f.write('\n')
        f.write("END\n")

def read_xyz(filename):
    """
    read xyz file and return the coordinates of atoms
    """
    with open(filename) as f:
        lines = f.readlines()
    num_atoms = int(lines[0])
    atoms = []
    coords = []
    for line in lines[2:]:
        atom,x,y,z = line.split()
        atoms.append(atom)
        coords.append([float(x),float(y),float(z)])
    return atoms,coords
   
def main(): 
    # path='/gpfs/projects/FrenkelGroup/kaif/FDMNES_cal/shape_proj/test_1_100_oblate/'
    xyzinp=glob("input/*.xyz")
    template_dir=config['template_dir']
    if not os.path.exists("FDMNESinp"):
           os.mkdir("FDMNESinp")
    else:
           shutil.rmtree("FDMNESinp")
           os.mkdir("FDMNESinp")
    j=0
    for i in tqdm(range(len(xyzinp)),total=len(xyzinp),desc=f"writing {xyzinp[j].split('/')[-1]}..."):
        write_FDMNESinp(template_dir,xyzinp[i],config['Absorber'],site=None)  
        j+=1
    
if __name__ == '__main__':
    main()
  




        
        
        
        
        
        
        
        
        
        
        
        
        



