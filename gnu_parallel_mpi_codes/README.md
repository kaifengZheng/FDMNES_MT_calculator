# FDMNES_MT_calculator
## 1. Propose
A multi-task FDMNES calculator can make life easier! In machine learning-based projects, people are often required to calculate thousands or more spectra in a very limited time. The traditional approach, which calculates one spectrum at each time, even if using a mpi-version calculator, is not feasible. The incredibly long time requires finishing thousands of spectra. I developed this code to run multiple simulations at the same time using allocated resources across cores.
## 2. Usage
### 2.1 Preparation
* config.toml
   * settings for running FDMNES
* input folder
   * contains all structure files(.xyz)
* main_write_from_xyz.py 
   * The code for writing the input files
* main_xyz.py
   * The main code for running multi-task FDMNES
* run_bash_write.sh
   * write commands for running main_xyz.py in command.txt, so that we can run the bash procedures in a sequence using gnu_parallel.
* run_bash_parallel.sh
   * run all processes in a sequence, including writing input files and running FDMNES.
* start_bash.sh
   * run bash procedures in a sequence.
* template.inp
   * header of FDMNES input file

### 2.2 steps
* writing FDMNES input files
```bash
python main_write_from_xyz.py
```
* running FDMNES on supercluster
```bash
chmod 777 start_bash.sh
./start_bash.sh
```
## 3. Dependency
* python=3.9
* toml
* json
* pymatgen
* tqdm
## 4. output
The outputs are stored in a self-created Output folder in JSON format.

<p align="center">
<img width="1300" height="200" src="https://github.com/kaifengZheng/FDMNES_package/gnu_parallel_mpi_codes/pics/workflow.png>
</p>
  
