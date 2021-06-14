#!/usr/bin/env python3

from KP.algorithms.DP import *
from KP.knapsack import generate
import random
import unittest

class TestDP(unittest.TestCase):
  def test_all_fits_in(self):
    kpi = generate(10, R = 100, type = "uncorr")
    capacity = kpi.wsum() #int(kpi.wsum() / 2)
    result = DPWB(kpi, capacity = capacity)
    tbl = result.profits_table
    sol = result.optima_single()
    self.assertTrue(all(item_number >= 0 for item_number in sol))
    self.assertTrue(all(item_number < kpi.N for item_number in sol))
    self.assertTrue(len(sol) == kpi.N)
    self.assertTrue(len(tbl) == (kpi.N + 1))
    self.assertTrue(len(tbl[0]) == (capacity + 1))
    self.assertEqual(tbl[kpi.N][capacity], kpi.psumint(sol))
    self.assertTrue(kpi.wsumint(sol) <= capacity)

  def test_multiple_global_optima(self):
    N = 10
    kpi = generate(N, R = 1, type = "uncorr")
    capacity = 3

    result = DPWB(kpi, capacity=capacity)
    sols = result.optima_all()
    for sol in sols:
      self.assertEqual(kpi.wsumint(sol), capacity)

    nsols = len(sols)
    self.assertEqual(nsols, int(N * (N - 1) * (N - 2) / 6))

    nsols = result.n_optima()
    self.assertEqual(nsols, int(N * (N - 1) * (N - 2) / 6))

  def test_multiple_global_optima_variants(self):
    N = 10
    for _ in range(25):
      kpi = generate(N, R = 1, type = "uncorr")
      capacity = 1000#int(kpi.wsum() / 2)
      result = DPWB(kpi, capacity=capacity)
      nsols1 = result.n_optima()
      nsols2 = len(result.optima_all())
      self.assertEqual(nsols1, nsols2)

  def test_all_global_optima_can_be_found_even_if_their_weights_are_different(self):
    # Simple instance where our global DP does not find all global optima
    kpi = KnapsackInstance(capacity = 6, weights = [6, 3, 2, 4], profits = [6, 3, 3, 1])
    sols = DPWB(kpi).optima_all()
    # optimal are [0] and [1,2] with profit 6 and weights 6 and 5 respectively
    self.assertEqual(len(sols), 2)

  def test_dp_profit_based_vs_dp_weight_based(self):
    N = 25
    for _ in range(25):
      kpi = generate(N, R = 100, type = "uncorr")
      capacity = round(kpi.wsum() / 2)
      wbres = DPWB(kpi, capacity).optima_single()
      pbres = DPPB(kpi, capacity).optima_single()
      # check if profits are equal
      self.assertEqual(kpi.psumint(pbres),  kpi.psumint(wbres))
      self.assertTrue(kpi.wsumint(pbres) <= kpi.wsumint(wbres))

  def test_dp_profit_based_fptas(self):
    N = 25
    for _ in range(25):
      kpi = generate(N, R = 100, type = "uncorr")
      capacity = round(kpi.wsum() / 4)
      eps = random.uniform(0.1, 0.5)
      pbres_exact = DPPB(kpi, capacity = capacity, eps = None).optima_single()
      pbres_approx = DPPB(kpi, capacity = capacity, eps = eps).optima_single()
      # check if approximation ratio is met
      self.assertTrue(kpi.psumint(pbres_approx) >= ((1 - eps) * kpi.psumint(pbres_exact)))

unittest.main()
