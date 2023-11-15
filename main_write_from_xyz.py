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
from scipy.spatial.distance import cdist




        
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
            f.write("Z_absorber\n")
            f.write(f"{atomic_num}\n\n")
        else:
            f.write("absorber\n")
            f.write(f"{site}\n\n")
        f.write("Radius\n")
        f.write(f"{np.round(radius_s(coords),1)}\n\n")
        f.write('Molecule\n')
        f.write("1   1   1   90   90   90\n")
        for i in range(len(atoms)):
            f.write(f"{Element(atoms[i]).Z} {coords[i][0]} {coords[i][1]} {coords[i][2]}\n")
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
def radius_s(coordinates):
    center=np.mean(coordinates,axis=0)
    r=np.max(cdist(coordinates,[center]))
    if type(r)==np.ndarray:
        r=r[0]
    return r+0.1 #slightly larger than the radius of the sphere
def write_from_restart():
    readfiles=glob(f"FDMNESinp/*.inp")
    readout=glob(f"output/*.json")
    out = []
    input = []
    for str1 in readout:
        out.append(str1.split('/')[1].split('.')[0])
    for i in range(len(readfiles)):
        if readfiles[i].split('/')[1].split('.')[0] in out:
            data=read_json(f"output/{readfiles[i].split('/')[1].split('.')[0]}.json")
            try:
                data["mu_conv"]
            except:
                input.append(readfiles[i])
        else:
            input.append(readfiles[i])
        if type(input)==str:
            input=[input]
    #print(input)
    print(out)
    print(readfiles[i].split('/')[1].split('.')[0])
    with open("run_files.txt","w") as f1:
        for inp in input:
            f1.write(inp+"\n") 

def main(): 
    # path='/gpfs/projects/FrenkelGroup/kaif/FDMNES_cal/shape_proj/test_1_100_oblate/'
    xyzinp=glob("input/*.xyz")
    template_dir=config['template_dir']
    restart=config['restart']
    if restart == False:
        if not os.path.exists("FDMNESinp"):
               os.mkdir("FDMNESinp")
        else:
               shutil.rmtree("FDMNESinp")
               os.mkdir("FDMNESinp")
        j=0
        for i in tqdm(range(len(xyzinp)),total=len(xyzinp),desc=f"writing {xyzinp[j].split('/')[-1]}..."):
            write_FDMNESinp(template_dir,xyzinp[i],config['Absorber'],site=None)  
            j+=1
        inp_files=glob("FDMNESinp/*.inp")
        with open("run_files.txt","w") as f1:
            for i in range(len(inp_files)):
                f1.write(inp_files[i]+"\n")
    else:
        write_from_restart()
if __name__ == '__main__':
    main()
  




        
        
        
        
        
        
        
        
        
        
        
        
        



