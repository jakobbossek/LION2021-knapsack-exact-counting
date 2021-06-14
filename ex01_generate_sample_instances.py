from KP.knapsack import *
import pprint
import csv

generators = ["uncorr", "wcorr", "scorr", "ascorr", "invscorr", "ss"]
L = 1
R = 250
n = 100

for generator in generators:
  outfilename = "data/example_instances/" + str(generator) + ".csv"
  kpi = generate(n=n, L=L, R=R, type=generator)
  kpi.save(outfilename)
