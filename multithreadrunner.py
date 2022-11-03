import click

def run(executable_name, max_threads):
    thread_nums = []
    threadnum = 1
    while threadnum < max_threads:
        thread_nums += threadnum
        threadnum *= 2
    
    runtimes = []
    for c in thread_nums:
        runtime = run_executable(executable_name, c)
        runtimes += (c, runtime)
    
    write_results(executable_name, runtimes)


if __name__=="__main__":
    run()