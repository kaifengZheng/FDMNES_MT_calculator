#! /use/bin bash
import pandas as pd
import numpy as np
import glob as glob
import json 
def read_json(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def write_table():
    readout=glob.glob(f"../output/*.json")
    out = []
    table=dict()
    for i in range(len(readout)):
        filename=readout[i].split('/')[-1].split('.')[0]
        data=read_json(readout[i])
        E=data['e_conv']
        table['E']=data['e_conv']
        try:
            table[filename]=data["mu_conv"]
        except:
            print(f"failed to export data: {filename}.")
    #print(input)
    table=pd.DataFrame(table)
    table.csv("Reg_particle_FDMNES.csv")

def main():
    write_table()

if __name__ == '__main__':
    main()
