import re
from scipy.interpolate import interp1d
import glob
import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import concurrent.futures as confu
from concurrent import futures
from tqdm import tqdm

parser=argparse.ArgumentParser(description="calculate average spectrum,defualt is using 1 core")
parser.add_argument('-n','--cores',type=int,default=1,help='the number of works')

args = parser.parse_args()
ncores=args.cores

def get_XAS_fdmnes(filename: str, w: int = 1) -> np.ndarray:
    """Reads the XAS data from a FDMNES output file

    Args:
        filename (str): FDMNES output file path
        w (int, optional): Weight of the XAS spectrum. Defaults to 1.

    Returns:
        XAS_spectrum(np.ndarray): XAS data. First column is the energy, second column is the normalized absorption coefficients.
    """

    fdmnes_data = np.loadtxt(filename, skiprows=1)
    fdmnes_data[:, 0] += fdmnes_energy_shift
    fdmnes_data[:, 1] /= fdmnes_scale_factors * w
    return fdmnes_data

def get_numbers(particle_name:str):
    data=np.loadtxt(f"../input/{particle_name}.xyz")
    return len(data)

def load_files(filename,i):
    particle=filename[i].split('/')[2].split('.')[0]
    with open(filename[i]) as f:
      data = json.load(f)
    Energy=np.array(data['e_conv'],dtype=float)
    mu=np.array(data['mu_conv'],dtype=float)
    n_atoms=get_numbers(particle)
    return particle,Energy,mu,n_atoms

print("reading data...\n")
output = dict()
Energy_record = []
fig, ax = plt.subplots()


filename = glob.glob("../output/*.json")
# now is only for xyz files
# structure_file = glob.glob("../input/*.xyz")

# data_record = dict()

# for i in tqdm(range(len(filename)), total=len(filename)):
#     with open(filename[i]) as f:
#         data = json.load(f)
#     name = filename[i].split("/")[2].split("_site")[0]
#     with open(f"../input/{name[:-5]}.xyz") as file1:
#         num_atoms = int(file1.readline())
#     print(num_atoms)
#     Energy = np.array(data["e_conv"], dtype=float)
#     if data_record == dict():
#         data_record["Energy"] = Energy
#     mu = np.array(data["mu_conv"], dtype=float) / num_atoms
#     Energy_record.append(Energy)
#     data_record[name] = mu
#     # ax.plot(Energy,mu,alpha=0.5)
#     # ax.set_xlim([Energy[0]-5,Energy[-1]+5])
#     # ax.set_ylim([-0.01,0.15])
#     print(f"mu_Energy_equ={len(Energy)==len(mu)} {name}")
# except:
#    continue
# Energy_record=np.array(Energy_record)
# Energy_min = [Energy_record[i][0] for i in range(len(Energy_record))]
# Energy_first = np.max(Energy_min)
# Energy_max = [Energy_record[i][-1] for i in range(len(Energy_record))]
# Energy_last = np.min(Energy_max)

print("reading data...\n")
output=dict()
Energy=[]
filename=glob.glob("../output/*.json")
with tqdm(total=len(filename)) as pbar:
    with confu.ThreadPoolExecutor(max_workers=ncores) as executor:
        jobs=[executor.submit(load_files,filename,i) for i in range(len(filename))]
        for job in futures.as_completed(jobs):
            Energy.append(job.result()[1])
            if job.result()[0] not in output.keys():
                output[job.result()[0]]=[{'E':job.result()[1],
                        'mu':job.result()[2],
                        'site':job.result()[3],
                        'n_sites':job.result()[4],
                        'cn':job.result()[5]}]
                #print(particle)
            else:
                output[job.result()[0]].append({'E':job.result()[1],
                        'mu':job.result()[2],
                        'site':job.result()[3],
                        'n_sites':job.result()[4],
                        'cn':job.result()[5]})
            pbar.update(1)
keys = list(output.keys())
E_grids=output[keys[0]][0]['E']
# print(keys)
#average
print("average...\n")
output_ave=dict()
output_ave["E"]=E_grids
for key in tqdm(output.keys()):
    sum1=np.zeros(len(output[key][0]['E']))
    ave=np.zeros(len(output[key][0]['E']))
    atoms=0

    for i in range(len(output[key])):
        sum1+=output[key][i]['mu']#/output[key][i]['n_sites']
        atoms+=output[key][i]['n_sites']
    print(f"{atoms} atoms in {key}")
    output_ave[key]=np.round(sum1/atoms,5)

print("plotting...\n")
output_ave=pd.DataFrame(output_ave)
output_ave.to_csv("../output_ave.csv",index=False)

data=pd.read_csv("../output_ave.csv")
fig,ax=plt.subplots()
for key in data.keys():
    if key!="E":
        ax.plot(data['E'],data[key],label=key)
# ax.set_xlim([11555,11620])
ax.set_xlabel("E(eV)")
ax.set_ylabel("$\mu$")
plt.title("average spectra")

#plt.show()
plt.savefig("../average.png")

