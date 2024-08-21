#!/usr/bin/env bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=47:59:59
#SBATCH --partition=extended-40core
#SBATCH --output=array_test.%N_%a.log
#SBATCH --job-name=fdmnes_8_all
#SBATCH --mail-user=kaifeng.zheng@stonybrook.edu
#SBATCH --mail-type=ALL

module load slurm
module load  python/3.9.7
#module load intel/oneAPI/2021.4

#module load  mpi/2021.4.0

module load gnu-parallel

export I_MPI_HYDRA_BOOTSTRAP=ssh
export JOBS_PER_NODE=$(($SLURM_CPUS_ON_NODE / $SLURM_CPUS_PER_TASK))
export WDIR=/gpfs/projects/FrenkelGroup/kaif/FDMNES_cal/Pt_shape_proj_7/particle_one_site/P_8_all
cd $WDIR
echo "============================================"
echo "SLURM_CPUS_PER_TASK=$SLURM_CPUS_PER_TASK"
echo "JOBS_PER_NODE=$JOBS_PER_NODE"
echo "============================================"

#EMPTY_CPUS=0
bash run_bash_write.sh $SLURM_CPUS_PER_TASK
#$SLURM_CPUS_PER_TASK
wait
rm hostfile
#echo $SLURM_JOB_NODELIST |sed s/\,/\\n/g > hostfile
scontrol show hostnames >> hostfile

#parallel -j 2 --wd $WDIR  --slf hostfile --joblog task.log --resume --progress <command.txt
parallel -j $JOBS_PER_NODE  --wd $WDIR  --joblog task.log --resume --progress <command.txt
wait
#$JOBS_PER_NODE 

