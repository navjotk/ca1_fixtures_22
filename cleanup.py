import click
import datetime
import csv
import os
import shutil
import shlex
from time import time
import subprocess
from mako.template import Template


def read_results(results_file):
    results = []
    with open(results_file) as ifile:
        reader = csv.DictReader(ifile)
        results = list(reader)
    return results


def run_command(command, cwd=None, shell=False):
    print("Executing command `%s`"%command)
    c = shlex.split(command)
    p = subprocess.Popen(c, cwd=cwd, shell=shell)
    return p.wait()


def generate_leaderboard(template_file, results, main_column, output_file, freq):
    leaderboard_template = Template(filename=template_file)
    time = datetime.datetime.now()
    timedelta = datetime.timedelta(hours=freq)
    results = sorted(results, key=lambda d: d[main_column])
    columns = list(results[0].keys())
    # Make main column the second column (first after ID)
    columns.insert(1, columns.pop(columns.index(main_column)))
    leaderboard_string = leaderboard_template.render(rows=results, columns=columns, time=str(time),
                                                     next_time=str(time+timedelta))

    with open(output_file, "w") as text_file:
        text_file.write(leaderboard_string)

    return output_file

def publish_file(output_file, git_repo):
    publish_dir = git_repo.split("/")[-1].split(".")[0]

    if not os.path.exists(publish_dir):
        run_command("git clone %s" % git_repo)
    else:
        run_command("git pull origin main")
    run_command("git checkout main", cwd=publish_dir)
    shutil.move(output_file, "%s/%s" % (publish_dir, output_file))
    run_command("git add %s" % output_file, cwd=publish_dir)
    run_command("git commit -m\"Update leaderboard\"", cwd=publish_dir)
    run_command("git push origin main", cwd=publish_dir)


@click.command()
@click.option('--template-file', required=True, help='The template file')
@click.option('--results-file', required=True, help='The results file')
@click.option('--output-file', required=True, help='The template file')
def run(template_file, results_file, output_file, main_column="avg_par_eff", freq=6,
        git_repo="https://navjotk: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@github.com/SciCoLab/ca2-leaderboard.git"):
    results = read_results(results_file)
    output_file = generate_leaderboard(template_file, results, main_column, output_file, freq)
    publish_file(output_file, git_repo)


if __name__=="__main__":
    run()