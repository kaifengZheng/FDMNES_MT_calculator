from glob import glob
import concurrent.futures as confu
import numpy as np
import json
import os
from tqdm import tqdm
import argparse
from concurrent import futures
import shutil
parser=argparse.ArgumentParser(description="check corrupted files")
parser.add_argument('-n','--cores',type=int,default=1,help='the number of works')
args = parser.parse_args()
ncores=args.cores

def check_files(filename,i):
    particle=filename[i].split('/')[2].split("_site")[0]
    try:
        with open(filename[i]) as f:
            data = json.load(f)
        Energy=np.array(data['e_conv'],dtype=float)
        mu=np.array(data['mu_conv'],dtype=float)
    except:
        os.remove(filename[i])
        print(f"{particle} is bad")
        delete+=1
        #print(f"{readout[i]} is corrupted and deleted\n")
        #print(f"deleted {delete} corrupted files\n")

readout=glob(f"../output/*.json")
out=[]

if type(readout)==str:
    readout=[readout]
delete=0
with tqdm(total=len(readout)) as pbar:
    with confu.ThreadPoolExecutor(max_workers=ncores) as executor:
        jobs=[executor.submit(check_files,readout,i) for i in range(len(readout))]
        for job in futures.as_completed(jobs):
            pbar.update(1)
#readout=glob(f"../output/*.json")

#for i in range(len(readout)):
#    out.append(readout[i].split('/')[2].split('.')[0])




#readin=glob("../input/*.xyz")
#for i in range(len(readin)):
#    namein=readin[i].split('/')[2].split('.')[0]
#    if namein not in out:
#       shutil.copy(readin[i],"../input/")

