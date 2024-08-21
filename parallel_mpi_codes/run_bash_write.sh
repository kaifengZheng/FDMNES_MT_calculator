#!/usr/bin/env bash

rm command.txt
while IFS= read -r line <&3; #add file desciptor to redirect  stdin to prevent conflicts.
  do
    echo "$line"
    #echo $nodeindex
    echo "python main_xyz.py -np $1 -in "$line""  >> command.txt  
    #echo $i
done 3< run_files.txt 

echo "success"
wait

