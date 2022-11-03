#!/bin/bash -l

# Specific course queue and max wallclock time
#SBATCH -p course -t 20 -c 40

# Defaults on Barkla (but set to be safe)
## Specify the current working directory as the location for executables/files
#SBATCH -D ./
## Export the current environment to the compute node
#SBATCH --export=ALL

# load modules
## intel compiler
module load compilers/intel/2019u5 

conda activate codegrade

% for submission in submissions:
python ${artifacts_path}/multithreadrunner.py ${submission}
% endfor

python ${artifacts_path}/cleanup.py $SLURM_JOB_ID