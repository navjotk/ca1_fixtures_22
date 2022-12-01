import click
import shlex
import subprocess
import portalocker
import csv
import os
import sys
from contexttimer import Timer
import portalocker

from writer import write_results
from executor import run_executable


@click.command()
@click.option('--basedir', default=None, help='Directory to find executables')
@click.option('--num-threads', default=40, help='Maximum number of threads')
@click.option('--executable', required=True, help="Name of executable to run")
@click.option('--identifier', required=True, help='Identify this submission')
@click.option('--results-file', required=True, help='Where to write the results')
def run(basedir, num_threads, executable, identifier, results_file):
    all_data = []
    if executable.find(",")>-1:
        e_full = executable.split(",")
        args = e_full[1:]
        e = e_full[0]
    else:
        args = None
        e = executable

    if basedir is None:
        basedir = "."

    e_full_path = os.path.join(basedir, e)

    runtime = run_executable(e_full_path, args, num_threads, num_runs=3)
    if runtime is None:
        print("Provided command is erroring out. Timings are meaningless. Moving on...")
        sys.exit(-1)
    
    results_to_write = {'id': identifier, 'executable': executable, 'threads': num_threads,
                        'runtime': runtime}
    write_results(results_to_write,
                  lambda x: (x['id'] == str(identifier) and
                             x['executable'] == str(executable) and
                             x['threads'] == str(num_threads)),
                  results_file)


if __name__=="__main__":
    run()