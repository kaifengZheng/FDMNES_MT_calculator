#!/usr/bin/env bash
rm -f *.log
rm -rf /gpfs/scratch/kaifzheng/fdmnes
#rm -rf output
rm -f hostname
mkdir /gpfs/scratch/kaifzheng/fdmnes
mkdir /gpfs/scratch/kaifzheng/fdmnes/calculation
#mkdir output
rm ar*
sbatch run_bash.sh  


