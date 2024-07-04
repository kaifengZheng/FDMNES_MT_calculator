#!/usr/bin/env bash

module load slurm
module load  python/3.9.7

NUM_NODES=1
CPU_PER_TASK=30
CPU_PER_PARTITION=30
#EMPTY_CPUS=0


nodeindex=0
rm hostname
scontrol show hostnames >> hostname

# filenum=$(ls -1 "input" | wc -l)


hostnum=$(cat hostname | wc -l)
let numcpus=$((NUM_NODES*CPU_PER_PARTITION))

let dividcpus=$((numcpus/CPU_PER_TASK))

# for ((i=0;i<$filenum;i++))
i=0
while IFS= read -r line;
  do
    if (( $nodeindex>=$NUM_NODES )); then
        let nodeindex=0
    fi
    echo $i 
    echo "using the $nodeindex th node"
    echo "$line"
    #echo $nodeindex 
    let "modu = ((((i+1)*CPU_PER_TASK)%CPU_PER_PARTITION))"
    
    if [ $hostnum -eq 1 ];then
        python main_xyz.py -np $CPU_PER_TASK -in "$line"  --hostfile hostname --host $nodeindex &
	wait
	echo "$line"
    else
	python main_xyz.py -np $CPU_PER_TASK -in "$line"  --hostfile hostname --host $nodeindex &
	if [ $((i%dividcpus)) -eq 0 -a $i -ne 0];then
            wait
        fi
	if [ $modu -eq 0 -a $i -ne 0 ]; then
            (( nodeindex += 1 ))
	fi
    fi
    ((i++))
    echo $i
done < run_files.txt
echo "success"
wait

