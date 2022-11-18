#!/bin/bash -l

# Specific course queue and max wallclock time
#SBATCH -t 60 -c 32 -p course

# Defaults on Barkla (but set to be safe)
## Specify the current working directory as the location for executables/files
#SBATCH -D ./
## Export the current environment to the compute node
#SBATCH --export=ALL

# load modules
## intel compiler
module load compilers/intel/2019u5 

conda activate codegrade

python ${artifacts_path}/filedownloader.py --file-list ${artifacts_path}/input_files_list.txt

python ${artifacts_path}/multithreadrunner.py --basedir ${submission_dict['path']} --max-threads 40 --executable "op1,input_64_512_960.dat,kernel_5.dat,output_64_512_960x5.dat" --executable "op2,a.dat,b.dat,c.dat" --identifier ${submission_dict['user']} --results-file results.csv

python ${artifacts_path}/cleanup.py --template-file ${artifacts_path}/table.tpl --results-file results.csv --output-file table.html --git-repo ${leaderboard_repo} --freq ${update_frequency}