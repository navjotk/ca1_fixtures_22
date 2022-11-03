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

% for submission_id, submission_path in submissions:
python ${artifacts_path}/multithreadrunner.py --basedir ${submission_path} --max-threads 40 --executable op1 --executable op2 --identifier ${submission_id} --results-file results.csv
% endfor

python ${artifacts_path}/cleanup.py --template-file ${artifacts_path}/table.tpl --results-file results.csv --output-file table.html --git-repo ${leaderboard_repo} --freq ${update_frequency}