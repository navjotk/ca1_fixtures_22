import click
import shlex
import subprocess
import portalocker
import csv
import os
import sys
from contexttimer import Timer


def run_executable(executable, args, num_threads, num_runs=3):
    command = executable
    
    if args is not None:
        command += " " + (" ").join(list(args))

    print("Command: %s" % command)

    c = shlex.split(command)

    env = {'OMP_NUM_THREADS': num_threads, 'KMP_AFFINITY': 'true'}
    
    timings = []
    for i in range(num_runs):
        with Timer() as t:
            p = subprocess.run(c, capture_output=True, text=True)
        if(p.returncode):
            print(p.stdout)
            return None
        timings.append(t.elapsed)
    
    return min(timings)

def get_results_row(all_data, identifier, precision=4):
    row = {'id': identifier}
    efficiencies = []
    for e, runtimes in all_data:
        single_thread_time = runtimes[0][1]
        for numthreads, runtime in runtimes:
            key = "%s_%d" % (e, numthreads)
            row[key] = round(runtime, precision)
            speedup = single_thread_time/runtime
            efficiency = round(speedup/numthreads, precision)
            efficiencies.append(efficiency)
    row['avg_par_eff'] = sum(efficiencies)/len(efficiencies)
    return row

def write_results(all_data, identifier, results_file):
    lock = portalocker.Lock(results_file)
    exists = os.path.exists(results_file)
    existing_results = []
    with lock:
        if os.path.exists(results_file):
            with open(results_file) as ifile:
                reader = csv.DictReader(ifile)
                existing_results = list(reader)
        
        existing_results = [x for x in existing_results if x['id']!=identifier]

        newrow = get_results_row(all_data, identifier)
        
        existing_results.append(newrow)

        with open(results_file, mode="w") as ofile:
                writer = csv.DictWriter(ofile, fieldnames=newrow.keys())
                writer.writeheader()
                for row in existing_results:
                    writer.writerow(row)



@click.command()
@click.option('--basedir', default=None, help='Directory to find executables')
@click.option('--max-threads', default=40, help='Maximum number of threads')
@click.option('--executable', multiple=True, help="Name of executable to run")
@click.option('--identifier', required=True, help='Identify this submission')
@click.option('--results-file', required=True, help='Where to write the results')
def run(basedir, max_threads, executable, identifier, results_file):
    thread_nums = []
    threadnum = 1
    while threadnum < max_threads:
        thread_nums.append(threadnum)
        threadnum *= 2
    
    all_data = []
    for e in executable:
        if e.find(",")>-1:
            e_full = e.split(",")
            args = e_full[1:]
            e = e_full[0]
        else:
            args = None

        if basedir is None:
            basedir = "."

        e_full_path = "%s/%s" % (basedir, e)
        runtimes = []
        for c in thread_nums:
            runtime = run_executable(e_full_path, args, c)
            runtimes.append((c, runtime))
        all_data.append((e, runtimes))
    
    write_results(all_data, identifier, results_file)


if __name__=="__main__":
    run()