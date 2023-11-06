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
import glob
import sys
import toml
from tqdm import tqdm



        
#inputs = sys.argv     


#ncores  = int(inputs[1])
#ind   = int(inputs[2])


#print(ind)

parser = argparse.ArgumentParser(description='calculation configuration')
parser.add_argument('-np','--ncores',type=int,help="number of cores")
parser.add_argument('-in','--inputfile',type=str,help="specific input file name")
parser.add_argument('--hostfile',type=str,help="The location of hostfile")
parser.add_argument('--host',type=int,help="assign specific host to run the program")
args = parser.parse_args()
ncores = args.ncores
input_file = args.inputfile
hostname=args.hostfile
host_ind=args.host
config = toml.load('config.toml')


def write_FDMNESinp(template_dir,pos_filename,CA,radius,site=None):
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
    return f"FDMNES_inp/{title}.inp",title

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

class FDMNES_cal:
    def __init__(self,config):
        self.scratch_path=config['scratch_path']#place to run the calculation
        self.exe_path=config['exe_path'] #place stored the executable file
        self.cleanup=config['cleanup'] #whether to delete the scratch folder after calculation
        self.cores=config['cores'] #number of cores to run the calculation
        self.tasks=config['tasks'] #tasks to run
        self.mpi_cmd=f"mpirun -np {self.cores}" #mpi command

#def fdmnes_calculator_mpi(js,node):
    def fdmnes_calculator_mpi(config,ncores,host_ind):

        '''
        # USAGE:
        with open('/data/software/FDMNES/fdmnes_tests/4_nospin/fdmnes.inp') as fi:
            fdmnesinp = fi.readlines()
        js =  {'task':'fdmnes_run', 'fdmnes_inp': fdmnesinp, 'ncores':12} 
        js_out = fdmnes_calculator_mpi(js)
        js_out
        '''
        
        #runtime parameters
        #try:
        #    ncores = js['ncores']
        #except:
        #    ncores=4
            
        # try:
        #     mpirun_cmd = js['mpirun_cmd']
        # except:
        #     mpirun_cmd = '/opt/intel/oneapi/mpi/2021.5.1/bin/mpirun'
        
        try:
            exe_path = js['exe_path']
        except:
            exe_path = '/gpfs/home/kaifzheng/software/parallel_fdmnes'

        try:
            cleanup = js['cleanup']
        except:
            cleanup = 'true'
            
        
        
        
        try:

            os.chdir(fdmnes_scratch_path)
            uid = 'fdmnes_'+''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=10))
            os.makedirs(uid,exist_ok=True)
            os.chdir(uid)
            
            print('Running FDMNES calculation at \n %s/%s \n using %d cores\n'%(fdmnes_scratch_path,uid,ncores))
            
            fi = open("fdmnes.inp", "w")
            for ii in js['fdmnes_inp']:
                fi.write(ii)
            fi.close()
            

            try:
                js['cif']
                cif = open("structure.cif", "w")
                for cc in js['cif']:
                    cif.write(cc)
                cif.close()
            except:
                pass
            




            #fdmnes wants this
            fi = open("fdmfile.txt", "w")
            fi.write('1\n')
            fi.write('fdmnes.inp\n')
            fi.close()          
            fi = open("hostfile","w")
            for hh in js['hostfile']:
                fi.write(hh)
            fi.close()
            exe_list = [
                'mpirun_fdmnes'                               #'fdmnes_mpi_linux64',
            ]

            start_time = time.time()  

            begin_time = time.time()
            
            host = js["hostfile"][host_ind][:-1]
            print(host)
            for e in exe_list:
                _ = subprocess.run(['HOST_NUM_FOR_MUMPS=4 bash %s/%s -np %d --hostfile %s --host %s >> fdmnes.out ' %(exe_path,e,ncores,'hostfile',host)],shell=True)
                print(_)
                #_ = subprocess.run(['srun -n %d %s/%s >> fdmnes.out' %(ncores,exe_path,e)],shell=True)
            # _ = subprocess.run(['srun --nodelist=%s -N 1 -n %d %s/%s >> fdmnes.out' %(node,ncores,exe_path,e)],shell=True)
                if _.returncode > 0:
                    print('error at %s'%e)
                    print(_)
                    break
            finish_time = time.time()
            print(f"running time:{finish_time-begin_time}")
            print("===================FINISHED======================\n\n\n")

            
        

            with open('fdmnes.inp') as f:
                fdmnesinp = f.readlines()
            with open('fdmnes.out') as f:
                fdmnesout = f.readlines()
            with open('fdmnes_bav.txt') as f:
                fdmnesbav = f.readlines()

            js = {
                'start_time': datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d__%H:%M:%S'),
                'finish_time': datetime.datetime.fromtimestamp(finish_time).strftime('%Y-%m-%d__%H:%M:%S'),
                'time_elapsed': finish_time - start_time,
                'fdmnesinp': fdmnesinp,
                'fdmnesout': fdmnesout,
                'fdmnesbav': fdmnesbav,
                'ncores': ncores,
                'exe_path': exe_path,
                }            
                


            # single site
            if os.path.isfile('fdmnes.txt'):
                with open('fdmnes.txt') as f:
                    fdmnestxt = f.readlines()
                # non-magnetic calculation
                if len(fdmnestxt[-1].split()) == 2:
                    js_new = {
                        'fname_fdmnestxt': 'fdmnes.txt',
                        'header_fdmnestxt': fdmnestxt[0:2],
                        'e':     [float(i.split()[0]) for i in fdmnestxt[2:]],
                        'mu':    [float(i.split()[1]) for i in fdmnestxt[2:]],
                        }
                    js.update(js_new)
                # magnetic calculation
                elif len(fdmnestxt[-1].split()) == 3:
                    js_new = {
                        'fname_fdmnestxt': 'fdmnes.txt',
                        'header_fdmnestxt': fdmnestxt[0:2],
                        'e':     [float(i.split()[0]) for i in fdmnestxt[2:]],
                        'mu_up':  [float(i.split()[1]) for i in fdmnestxt[2:]],
                        'mu_dw':  [float(i.split()[2]) for i in fdmnestxt[2:]],
                        'mu':  [(float(i.split()[1])+float(i.split()[2])) for i in fdmnestxt[2:]],
                        }
                    js.update(js_new)


            # multiple sites
            else:
 
                outputs = glob.glob('fdmnes_*.txt')

                for i in outputs:
                    try:
                        t = int(i.split('_')[1].split('.txt')[0])
                        
                        with open('fdmnes_%d.txt'%t) as f:
                            fdmnestxt = f.readlines()
                                
                        # non-magnetic calculation
                        if len(fdmnestxt[-1].split()) == 2:
                            js_new = {
                                'fname_fdmnestxt_%d'%t: i,
                                'header_fdmnestxt_%d'%t: fdmnestxt[0:2],
                                'e_%d'%t:     [float(i.split()[0]) for i in fdmnestxt[2:]],
                                'mu_%d'%t:    [float(i.split()[1]) for i in fdmnestxt[2:]],
                                }
                            js.update(js_new)

                        # magnetic calculation
                        elif len(fdmnestxt[-1].split()) == 3:
                            js_new = {
                                'fname_fdmnestxt_%d'%t: i,
                                'header_fdmnestxt_%d'%t: fdmnestxt[0:2],
                                'e_%d'%t:     [float(i.split()[0]) for i in fdmnestxt[2:]],
                                'mu_up_%d'%t:  [float(i.split()[1]) for i in fdmnestxt[2:]],
                                'mu_dw_%d'%t:  [float(i.split()[2]) for i in fdmnestxt[2:]],
                                'mu_%d'%t:  [(float(i.split()[1])+float(i.split()[2])) for i in fdmnestxt[2:]],
                                }
                            js.update(js_new)  

                    except:
                        pass            





                
            if os.path.isfile('fdmnes_conv.txt'):
                with open('fdmnes_conv.txt') as f:
                    fdmnestxt_conv = f.readlines()
                js_new = {
                    'fname_fdmnesconvtxt': 'fdmnes_conv.txt',
                    'header_fdmnesconvtxt': fdmnestxt[0:1],
                    'e_conv':     [float(i.split()[0]) for i in fdmnestxt_conv[1:]],
                    'mu_conv':    [float(i.split()[1]) for i in fdmnestxt_conv[1:]],
                    }
                js.update(js_new)


            os.chdir('..')

            if cleanup == 'true':
                shutil.rmtree(uid)
                
                
            return js


        except Exception as exc:
            print('something is wrong')
            print(exc)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
def main(): 
    # path='/gpfs/projects/FrenkelGroup/kaif/FDMNES_cal/shape_proj/test_1_100_oblate/'
    if config['temp_path'][-1]!='/':
        path=config['temp_path']+config['foldername']
    else:
        path=config['temp_path']+'/'+config['foldername']
    os.chdir(path)

    # input_files=glob.glob("input/*.inp")
    with open(input_file) as fi:
        fdmnesinp = fi.readlines()
    with open(hostname) as fi:
        hn=fi.readlines() 
    js_in  = {'fdmnes_inp': fdmnesinp,"hostfile":hn,'cleanup':'false'}        

    print(f"Running calculation using {input_file}")
    js_out =fdmnes_calculator_mpi(js_in,ncores,host_ind)

    os.chdir(path)
    pathlen = 10
    with open(path+'js/js_'+input_file[pathlen:-4]+'.json', 'w') as f:
        json.dump(js_out, f)
    
if __name__ == '__main__':
    main()
  




        
        
        
        
        
        
        
        
        
        
        
        
        



