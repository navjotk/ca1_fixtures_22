import click
import shlex
import subprocess
import portalocker
import csv
import os
from contexttimer import Timer


def run_executable(executable, num_threads, num_runs=3):
    command = "OMP_NUM_THREADS=%d KMP_AFFINITY=true %s" % (num_threads, executable)
    c = shlex.split(command)
    timings = []
    for i in range(num_runs):
        with Timer() as t:
            p = subprocess.Popen(c, shell=True)
            p.wait()
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
@click.option('--basedir', default="", help='Directory to find executables')
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
        e_full_path = "%s/%s" % (basedir, e)
        runtimes = []
        for c in thread_nums:
            runtime = run_executable(e_full_path, c)
            runtimes.append((c, runtime))
        all_data.append((e, runtimes))
    
    write_results(all_data, identifier, results_file)


if __name__=="__main__":
    run()