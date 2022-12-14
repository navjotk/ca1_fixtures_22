import pathlib
import os
from mako.template import Template
from executor import run_command


def submit_slurm_job(commands, template_file, num_cores=1,
                     num_tasks=1, time_limit=1, partition="course",
                     cwd=None, vars=None):
    if vars is None:
        vars = {}
    
    if cwd is None:
        cwd = pathlib.Path().resolve()
    
    slurm_file_template = Template(filename=template_file)

    submission_file_string = slurm_file_template.render(commands=commands,
                                                        num_cores=num_cores,
                                                        num_tasks=num_tasks,
                                                        time_limit=time_limit,
                                                        partition=partition,
                                                        vars=vars)

    target_slurm_filename = os.path.join(cwd, 'submission.sh')

    with open(target_slurm_filename, "w") as text_file:
        text_file.write(submission_file_string)

    job_id = call_slurm(target_slurm_filename, cwd)

    os.remove(target_slurm_filename)

    return job_id


def call_slurm(slurm_file, context_dir):
    p = run_command("sbatch --nice \"%s\"" % slurm_file, cwd=context_dir)
    output = p.stdout.decode('utf-8')
    print(output)
    parts_of_output = output.split(" ")
    job_id = (parts_of_output[-1]).strip()
    assert(job_id.isnumeric())
    return int(job_id)


def run():
    job_id = submit_slurm_job(["echo Hi"], "slurm_template.tpl")


if __name__=="__main__":
    run()