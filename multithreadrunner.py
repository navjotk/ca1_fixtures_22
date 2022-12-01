import click
import portalocker
import csv
import os
import sys
import portalocker

from writer import write_results
from executor import run_executable

def get_results_row(all_data, identifier, precision=3):
    row = {'id': identifier}
    efficiencies = []
    print(all_data)
    for e, runtimes in all_data:
        print("*")
        print(runtimes)
        single_thread_time = runtimes[0][1]
        for numthreads, runtime in runtimes:
            key = "%s_%d" % (e, numthreads)
            row[key] = round(runtime, precision)
            speedup = single_thread_time/runtime
            efficiency = round(speedup/numthreads, precision)
            if numthreads > 1:
                efficiencies.append(efficiency)
    print(efficiencies)
    row['avg_par_eff'] = round(sum(efficiencies)/len(efficiencies), precision)
    return row


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
    thread_nums = list(reversed(thread_nums))
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
        try:
            for c in thread_nums:
                runtime = run_executable(e_full_path, args, c)
                if runtime is None:
                    print("Provided command is erroring out. Timings are meaningless. Moving on...")
                    raise Exception("One executable errors. Maybe another one works")
                runtimes.append((c, runtime))
        except Exception:
            continue
        all_data.append((e, runtimes))
    
    results_to_write = get_results_row(all_data, identifier)
    write_results(results_to_write, lambda x: return  x['id']==identifier, results_file)


if __name__=="__main__":
    run()