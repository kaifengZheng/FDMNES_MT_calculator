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




print("reading data...\n")
output=dict()
Energy=[]
fig,ax=plt.subplots()
filename=glob.glob("../output/*.json")
for i in  tqdm(range(len(filename)),total=len(filename)):
    try:
        with open(filename[i]) as f:
            data=json.load(f)
        Energy=np.array(data['e'])
        mu=np.array(data['mu'])
        ax.plot(Energy,mu,alpha=0.5)
        ax.set_xlim([3,50])
        ax.set_ylim([-0.01,0.15])
    except:
        continue
plt.savefig('average.png')





