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
from pymatgen.core import Structure, Element,Molecule
import concurrent.futures as confu
from glob import glob
import sys
import toml
from tqdm import tqdm
from scipy.spatial.distance import cdist
import pymatgen.symmetry.analyzer




        
#inputs = sys.argv     


#ncores  = int(inputs[1])
#ind   = int(inputs[2])


#print(ind)
config = toml.load('config.toml')

def write_FDMNESinp(template_dir,pos_filename,CA,site=None,symmetry=False):
    """
    Writing FDMNES input file from xyz file
    :param template_dir: the directory of the template file
    :param pos_filename: the directory of the xyz file
    :param CA: the symbol of absorbing atom
    :param site: the index of absorbing atom
    :param symmetry: whether considering the symmetry of the molecule and calculate the XANES of each site or not
    """
    if symmetry == False:
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
    if symmetry == True:
        unique_index,numbers = equ_sites_pointgroup(pos_filename)
        for j in range(len(unique_index)):
            atomic_num=Element(CA).Z
            with open(template_dir) as f:
                template = f.readlines()
            title=pos_filename.split('.')[0].split('/')[-1]
            atoms,coords=read_xyz(pos_filename)
            with open(f"FDMNESinp//{title}_site_{unique_index[j]}_m_{numbers[j]}.inp",'w') as f:
                # site index from 0, _m_ is the number of equivalent sites.
                f.write(f"TITLE {title}_site.{unique_index[j]}_m_{numbers[j]}\n")
                f.writelines(template)
                f.write('\n\n')
                f.write("Absorber\n")
                f.write(f"{unique_index[j]+1}\n\n")
                # f.write("Radius\n")
                # f.write(f"{np.round(radius_s(coords),1)}\n\n")
                f.write('Molecule\n')
                f.write("1   1   1   90   90   90\n")
                for i in range(len(atoms)):
                    f.write(f"{Element(atoms[i]).Z} {coords[i][0]} {coords[i][1]} {coords[i][2]}\n")
                f.write('\n')
                f.write("END\n")
    
def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

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
    """
    Calculate radius used to calculate FDMNES spectra, which is the input of Radius card in FDMNES inputfile.
    """
    center=np.mean(coordinates,axis=0)
    r=np.max(cdist(coordinates,[center]))
    if type(r)==np.ndarray:
        r=r[0]
    return r+0.5 #slightly larger than the radius of the sphere
def write_from_restart():
    """
    If there is a colipse in the calculation and cannot finish all the calculation, using this function can rewrite the run_files.txt
    file to run the rest of the calculations.
    """
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
def equ_sites(CA:str,labels,natoms,positions,cutoff,randomness=4):
    """
    :param positions: coordinates
    :param cutoff:    cutoff distance defined by mutiple scattering radius
    :return:          non-equ position indexes
    """
    # cutoff method
    def duplicates(lst, item):
        """
        :param lst: the whole list
        :param item: item which you want to find the duplication in the list
        :return: the indexes of duplicate items
        """
        return [i for i, x in enumerate(lst) if x == item]
    
    caatoms=[i for i, e in enumerate(labels) if e == CA]

    dis_all =  np.around(cdist(np.array(positions),np.array(positions)[caatoms]),decimals=randomness)
    dis_all.sort(axis=1)
    dis_cut = [list(dis_all[i][dis_all[i] < cutoff]) for i in range(len(dis_all))]
    dup = []
    for i in range(len(dis_cut)):
        dup.append(duplicates(dis_cut, dis_cut[i])[0])
    #unique_index = list(set(dup))  # set can delete all duplicated items in a list
    unique_index = dict()
    for i in range(len(dup)):
        if dup[i] in unique_index:
            unique_index[dup[i]].append(i)
        else:
            unique_index.update({dup[i]:[i]})
    # formula_text
    formula = '$'
    for i,(k,v) in enumerate(natoms.items()):
        formula = formula + k + '_{' + str(int(v)) + '}'
    formula = formula + '$'
    # sort it using sorted method. Do not use list.sort() method, because it returns a nonetype.
    #unique_index = np.array(sorted(unique_index))
    #print("number of atoms: {}".format(len(positions)))
    #print("number of unique atoms: {}".format(len(atom_index))) #
    
    return unique_index,formula
def equ_sites_pointgroup(pos_dir):
    mol=Molecule.from_file(pos_dir)
    pointgroup=pymatgen.symmetry.analyzer.PointGroupAnalyzer(mol).get_equivalent_atoms()['eq_sets']
    keys=list(pointgroup.keys())
    num_sites=[len(pointgroup[keys[i]]) for i in range(len(keys))]
    return keys, num_sites

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
            write_FDMNESinp(template_dir,xyzinp[i],config['Absorber'],config['site_absorber'],site=None)  
            j+=1
        inp_files=glob("FDMNESinp/*.inp")
        with open("run_files.txt","w") as f1:
            for i in range(len(inp_files)):
                f1.write(inp_files[i]+"\n")
    else:
        write_from_restart()
if __name__ == '__main__':
    main()
  




        
        
        
        
        
        
        
        
        
        
        
        
        



