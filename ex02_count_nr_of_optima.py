from KP.knapsack import *
from KP.algorithms.DP import DPWB
import pprint
import random
import csv
import itertools
from joblib import Parallel, delayed # pip install joblib
import multiprocessing

'''
FINAL EXPERIMENTS
===

We want to vary:
* Knapsack instance generator: uncorr, scorr, awcorr, ...
* Number of items n
* Capacity limit W
* Range of items, i.e. L and R?
  -> Since all generators output integer values with (R-L) small
  we can expect much more global optima.

We should repeat for each combination of the parameters ...
* r >= 25 times with new instances. Maybe even r=100

SETUP
===

I guess there is no need for highly parallel experimentation.
However, we should go for local multi-core parallelization
(subprocess to the rescue!)
To this end, instead of nested loops, we should lazily iterate
over a collection of tuples/lists (n, r, R, L, type, ...) and
call a run_experiment function which also deals with output.
'''
if __name__ == "__main__":
  # reproducibility
  random.seed(1)

  # parallelization
  n_cpus = multiprocessing.cpu_count()

  # Number of items
  ns = [k * 10 for k in range(5, 51, 5)]

  # Upper bound for weight and profit sampling
  Ls = 1 # lower bound is fixed/constant
  Rs = [50, 100, 250]

  # Capacity factor
  H = 11
  h = list(range(1, H+1))

  # generators
  generators = ["uncorr", "wcorr", "scorr", "ascorr", "invscorr", "ss"]

  # Number of runs
  runs = list(range(1, 26))

  # Names of fields in experimental setup
  expfields = ["generator", "R", "n", "run", "h"]

  experiments = itertools.product(generators, Rs, ns, runs, h)

  def runExperiment(expnumber, expsetup):
    expsetup = dict(zip(expfields, expsetup))
    outfilename = "data/output/raw/" + str(expnumber) + ".csv"
    with open(outfilename, 'w', newline='') as outfile:
      writer = csv.writer(outfile)
      #writer.writerow(["generator", "L", "R", "n", "h", "run", "nsols"])
      kpi = generate(n=expsetup["n"], L=Ls,  R=expsetup["R"], type=expsetup["generator"])
      # set capacity
      capacity = (int)((expsetup["h"]/(H+1)) * kpi.wsum())
      nsols = DPWB(kpi, capacity=capacity).n_optima()
      print(".", end="", flush=True)
      row = [expsetup["generator"], Ls, expsetup["R"], expsetup["n"], expsetup["h"], expsetup["run"],nsols]
      writer.writerow(row)

  print("Starting experiments on {0} cores...\n".format(n_cpus))
  Parallel(n_jobs=n_cpus)(delayed(runExperiment)(expnumber, expsetup) for expnumber, expsetup in enumerate(experiments))

def source(filepath):
  exec(open(filepath).read())
