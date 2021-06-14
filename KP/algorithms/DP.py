from KP.knapsack import KnapsackInstance
import queue
import math

class DPWBSolution:
  '''
  Dynamic Programming Weight-Based (WB) approach solution object:

  Args:
    kpi (KnapsackInstance): Object of class KP.KnapsackInstance.KnapsackInstance
    capactiy (int): Knapsack capactiy
    profits_table: table m(i, j) which is the maximum profit reachable
    with items {1,...,i} and maximum weight j.
    nsols_table: entry c(i, j) indicates the number of solutions with maximum profit m(i,j) which can be reached by items {1,...,i} and maximum wieight j.
  Returns:
    Object of type DPWBSolution
  '''
  def __init__(self, kpi, capacity, profits_table, nsols_table):
    self.kpi = kpi
    self.profits_table = profits_table
    self.nsols_table = nsols_table
    self.N = kpi.N
    self.capacity = capacity

  def n_optima(self):
    return self.nsols_table[self.N][self.capacity]

  def optima_single(self):
    # We want just a single global optimum
    reconstruction = []
    i = self.kpi.N
    j = self.capacity
    items = list(self.kpi.getItems())

    while i > 0:
      # traceback in the table starting from tbl[N, capacity]
      if self.profits_table[i][j] != self.profits_table[i - 1][j]:
        reconstruction.append(i - 1)
        j -= items[i - 1][0]
      i -= 1

    return reconstruction

  def optima_all(self):
    # We want ALL global optima
    reconstruction = []
    i = self.kpi.N
    j = self.capacity
    items = list(self.kpi.getItems())

    count = 0
    # we store partially reconstructed packing plans in a queue
    Q = queue.Queue()
    Q.put((self.kpi.N, self.capacity, []))
    while not Q.empty():
      i, j, packing = Q.get()
      # classic reconstruction starts
      while i > 0:
        if self.profits_table[i][j] != self.profits_table[i - 1][j]:
          # item was packed, i.e. self.profits_table[i-1][j] < self.profits_table[i, j]
          packing.append(i - 1)
          j -= items[i - 1][0]
        elif (j - items[i - 1][0] >= 0) and (self.profits_table[i][j] == (self.profits_table[i - 1][j - items[i-1][0]] + items[i-1][1])):
          # not packing item results in the same profit as with items {0, ...,  n-2}?
          partialPacking = packing[:]  # make copy
          partialPacking.append(i - 1)
          Q.put((i - 1, j - items[i - 1][0], partialPacking))
        i -= 1
      count += 1
      reconstruction.append(packing)

    return reconstruction

  def solutions_sample(self, k, replace=True):
    assert 1 <= k
    pass


def DPWB(kpi, capacity=None):#, multiGlobal=True, countOnly=False):
  '''
  Dynamic Programming algorithm for the 0-1 Knapsack Problem (KP)

  Args:
    kpi (KnapsackInstance): Object of class KP.KnapsackInstance.KnapsackInstance
    capacity (int)        : Knapsack capacity, i.e. maximum weight of packed items. Defaults
    to the capacity of KI if None.
  Returns:
    An object of class DPSolution
  '''
  if capacity is None:
    capacity = kpi.capacity

  # (w_i, p_i)
  items = list(kpi.getItems())

  # init table
  tbl = [[0] * (capacity + 1) for _ in range(kpi.N + 1)]
  nsols = [[1] * (capacity + 1) for _ in range(kpi.N + 1)]

  for i, (weight, profit) in enumerate(items):
    i += 1
    for cap in range(capacity + 1):
      if (weight > cap):
        # (i-1)-th element does not fit in
        tbl[i][cap] = tbl[i - 1][cap]
        nsols[i][cap] = nsols[i - 1][cap]
      else:
        # otherwise check if it is of benefit to pack the item or not
        packOptionA = tbl[i - 1][cap]
        packOptionB = tbl[i - 1][cap - weight] + profit

        if (packOptionA == packOptionB):
          tbl[i][cap] = packOptionA
          nsols[i][cap] = nsols[i - 1][cap] + nsols[i - 1][cap - weight]
        elif (packOptionA > packOptionB):
          tbl[i][cap] = packOptionA
          nsols[i][cap] = nsols[i - 1][cap]
        else:
          tbl[i][cap] = packOptionB
          nsols[i][cap] = nsols[i - 1][cap - weight]

  return DPWBSolution(kpi=kpi, capacity=capacity, profits_table=tbl, nsols_table=nsols)


# PROFIT-BASED-APPROACH TO COUNT ALL OPTIMA
# ===
# I.e. we build and (n, nP) table instead of a (n, W) table.
# Under construction!
#
# Issues to solve:
# * It is not possible to modify this approach as simple as it
#   is for the (n,W)-approach.
# * How to reconstruct all solutions? And since the starting point
#   is not always the same, how to we update in case of sampling
#   without replacement?

class DPPBSolution:
  def __init__(self, kpi, capacity, profits_table, eps):
    self.kpi = kpi
    self.profits_table = profits_table
    self.N = kpi.N
    self.capacity = capacity
    self.profit_limit = self.N * max(kpi.profits)
    self.eps = eps

  def optima_single(self):
    # We want just a single global optimum
    reconstruction = []
    i = self.kpi.N
    j = self.profit_limit
    items = list(self.kpi.getItems())

    # determine maximal profit j such that profits_table[N, j] <= W
    j = max([k for k in range(self.profit_limit + 1) if self.profits_table[self.N][k] <= self.capacity])

    while i > 0:
      # traceback in the table starting from tbl[N, capacity]
      if self.profits_table[i][j] != self.profits_table[i - 1][j]:
        reconstruction.append(i - 1)
        j -= items[i - 1][1]  # subtract profit
      i -= 1

    return reconstruction


def DPPB(kpi, capacity = None, eps = None):
  '''
  Dynamic Programming algorithm for the 0-1 Knapsack Problem (KP)

  Args:
    kpi (KnapsackInstance): Object of class KP.KnapsackInstance.KnapsackInstance
    capacity (int)        : Knapsack capacity, i.e. maximum weight of packed items. Defaults
    to the capacity of KI if None.
    eps (float): Number between (0,1) for FPTAS.
  Returns:
    An object of class DPSolution
  '''
  if capacity is None:
    capacity = kpi.capacity

  if eps is not None:
    assert(eps > 0 and eps < 1)
    kpi = kpi.scale_down_profits(eps)

  # (w_i, p_i)
  items = list(kpi.getItems())

  # maximum profif
  N = kpi.N
  P = max(kpi.profits)  # TODO: for 0-1 KP sum(kpi.profits) should also be fine
  profit_limit = N * P

  # init table(s)
  # Each row: [0, Inf, Inf, ..., Inf]
  tbl = [[0] + [math.inf] * (profit_limit) for _ in range(N + 1)]
  nsols = [[1] + [0] * (profit_limit + 1) for _ in range(N + 1)]

  for i, (weight, profit) in enumerate(items):
    i += 1
    for p in range(profit_limit + 1):
      if (profit > p):
        # (i-1)-th element does not fit in
        tbl[i][p] = tbl[i - 1][p]
      else:
        # otherwise check if it is of benefit to pack the item or not
        packOptionA = tbl[i - 1][p]
        packOptionB = tbl[i - 1][p - profit] + weight

        if (packOptionA == packOptionB):
          tbl[i][p] = packOptionA
        elif (packOptionA < packOptionB):
          tbl[i][p] = packOptionA
        else:
          tbl[i][p] = packOptionB

  return DPPBSolution(kpi = kpi, capacity = capacity, profits_table = tbl, eps = eps)


# def DPBCK_without_DPSolutionObject(kpi, capacity=None, multiGlobal=True, countOnly=False):
#   '''
#   Dynamic Programming algorithm for the 0-1 Knapsack Problem (KP)

#   Args:
#     kpi (KnapsackInstance): Object of class KP.KnapsackInstance.KnapsackInstance
#     capacity (int)       : Knapsack capacity, i.e. maximum weight of packed items. Defaults
#     to the capacity of KI if None.
#     multiGlobal (bool)   : Should only one packing be reconstructed or all?
#     Defaults to False.
#     countOnly (bool)      : Should only the number of globally opimal packings be returned?
#     Defaults to False. Only relevant if multiGlobal=True.

#   Returns:
#     Both the DP packing table and a list of packed items (if multiglobal = False) or
#     a list of lists of packed items (if multiGlobal = True). If countOnly=True just a single
#     scalar is returned, namely the number of global optima.
#   '''
#   if capacity is None:
#     capacity = kpi.capacity

#   # (w_i, p_i)
#   items = list(kpi.getItems())

#   # init table
#   tbl = [[0] * (capacity + 1) for _ in range(kpi.N + 1)]
#   nsols = [[1] * (capacity + 1) for _ in range(kpi.N + 1)]

#   for i, (weight, profit) in enumerate(items):
#     i += 1
#     for cap in range(capacity + 1):
#       if (weight > cap):
#         # (i-1)-th element does not fit in
#         tbl[i][cap] = tbl[i - 1][cap]
#         nsols[i][cap] = nsols[i - 1][cap]
#         # nsols[i][cap] = nsols[i - 1][cap] + tbl[i - 1][cap - weight]

#         # if (((cap - weight) > 0) and (tbl[i - 1][cap - weight] == tbl[i - 1][cap])):
#         #   nsols[i][cap] = nsols[i - 1][cap] + tbl[i - 1][cap - weight]
#       else:
#         # otherwise check if it is of benefit to pack the item or not
#         packOptionA = tbl[i - 1][cap]
#         packOptionB = tbl[i - 1][cap - weight] + profit

#         if (packOptionA == packOptionB):
#           tbl[i][cap] = packOptionA
#           nsols[i][cap] = nsols[i - 1][cap] + nsols[i - 1][cap - weight]
#         elif (packOptionA > packOptionB):
#           tbl[i][cap] = packOptionA
#           nsols[i][cap] = nsols[i - 1][cap]
#         else:
#           tbl[i][cap] = packOptionB
#           nsols[i][cap] = nsols[i - 1][cap - weight]
#         #tbl[i][cap] = max(packOptionA, packOptionB)

#   if not multiGlobal:
#     # We want just a single global optimum
#     reconstruction = []
#     i = kpi.N
#     j = capacity
#     while i > 0:
#       # traceback in the table starting from tbl[N, capacity]
#       if tbl[i][j] != tbl[i - 1][j]:
#         reconstruction.append(i - 1)
#         j -= items[i - 1][0]
#       i -= 1
#   else:
#     # We want ALL global optima
#     reconstruction = []
#     count = 0
#     # we store partially reconstructed packing plans in a queue
#     Q = queue.Queue()
#     Q.put((kpi.N, capacity, []))
#     while not Q.empty():
#       i, j, packing = Q.get()
#       # classic reconstruction starts
#       while i > 0:
#         if tbl[i][j] != tbl[i - 1][j]:
#           # item was packed, i.e. tbl[i-1][j] < tbl[i, j]
#           packing.append(i - 1)
#           j -= items[i - 1][0]
#         elif (j - items[i - 1][0] >= 0) and (tbl[i][j] == (tbl[i - 1][j - items[i-1][0]] + items[i-1][1])):
#           # not packing item results in the same profit as with items {0, ...,  n-2}?
#           partialPacking = packing[:]  # make copy
#           partialPacking.append(i - 1)
#           Q.put((i - 1, j - items[i - 1][0], partialPacking))

#         i -= 1
#       if countOnly:
#         count += 1
#       else:
#         #TODO: actually we want only a list of {0,1}^N or {1,...,N} subset of [N]
#         reconstruction.append(packing)

#   #reconstruction.reverse()
#   if countOnly:
#     return nsols[kpi.N][capacity]
#     #return count

#   return tbl, reconstruction


# PROFIT-BASED-APPROACH TO COUNT ALL OPTIMA
# ===
# I.e. we build and (n, nP) table instead of a (n, W) table.
# Under construction!
#
# Issues to solve:
# * It is not possible to modify this approach as simple as it
#   is for the (n,W)-approach.
# * How to reconstruct all solutions? And since the starting point
#   is not always the same, how to we update in case of sampling
#   without replacement?

# class DPPBSolution:
#   def __init__(self, kpi, capacity, profits_table, nsols_table):
#     self.kpi = kpi
#     self.profits_table = profits_table
#     self.nsols_table = nsols_table
#     self.N = kpi.N
#     self.capacity = capacity
#     self.profit_limit = self.N * max(kpi.profits)

#   def n_optima(self):
#     return self.nsols_table[self.N][self.profit_limit]

#   def optima_single(self):
#     # We want just a single global optimum
#     reconstruction = []
#     i = self.kpi.N
#     j = self.profit_limit
#     items = list(self.kpi.getItems())

#     while i > 0:
#       # traceback in the table starting from tbl[N, capacity]
#       if self.profits_table[i][j] != self.profits_table[i - 1][j]:
#         reconstruction.append(i - 1)
#         j -= items[i - 1][1]  # subtract profit
#       i -= 1

#     return reconstruction

#   def optima_all(self):
#     # We want ALL global optima
#     reconstruction = []
#     i = self.kpi.N
#     j = self.profit_limit
#     items = list(self.kpi.getItems())

#     count = 0
#     # we store partially reconstructed packing plans in a queue
#     Q = queue.Queue()
#     Q.put((self.kpi.N, self.profit_limit, []))
#     while not Q.empty():
#       i, j, packing = Q.get()
#       # classic reconstruction starts
#       while i > 0:
#         if self.profits_table[i][j] != self.profits_table[i - 1][j]:
#           # item was packed, i.e. self.profits_table[i-1][j] < self.profits_table[i, j]
#           packing.append(i - 1)
#           j -= items[i - 1][1]
#         elif (j - items[i - 1][1] >= 0) and (self.profits_table[i][j] == (self.profits_table[i - 1][j - items[i-1][1]] + items[i-1][0])):
#           # not packing item results in the same profit as with items {0, ...,  n-2}?
#           partialPacking = packing[:]  # make copy
#           partialPacking.append(i - 1)
#           Q.put((i - 1, j - items[i - 1][1], partialPacking))
#         i -= 1
#       count += 1
#       reconstruction.append(packing)

#     return reconstruction

#   def solutions_sample(self, k, replace=True):
#     assert 1 <= k
#     pass


# def DP(kpi, capacity=None):
#   '''
#   Dynamic Programming algorithm for the 0-1 Knapsack Problem (KP)

#   Args:
#     kpi (KnapsackInstance): Object of class KP.KnapsackInstance.KnapsackInstance
#     capacity (int)        : Knapsack capacity, i.e. maximum weight of packed items. Defaults
#     to the capacity of KI if None.
#   Returns:
#     An object of class DPSolution
#   '''
#   if capacity is None:
#     capacity = kpi.capacity

#   # (w_i, p_i)
#   items = list(kpi.getItems())

#   # maximum profif
#   N = kpi.N
#   P = max(kpi.profits)  # TODO: for 0-1 KP sum(kpi.profits) should also be fine
#   profit_limit = N * P

#   # init table(s)
#   # Each row: [0, Inf, Inf, ..., Inf]
#   tbl = [[0] + [math.inf] * (profit_limit) for _ in range(N + 1)]
#   nsols = [[1] + [0] * (profit_limit + 1) for _ in range(N + 1)]

#   for i, (weight, profit) in enumerate(items):
#     i += 1
#     for p in range(profit_limit + 1):
#       if (profit > p):
#         # (i-1)-th element does not fit in
#         tbl[i][p] = tbl[i - 1][p]
#         nsols[i][p] = nsols[i - 1][p]
#       else:
#         # otherwise check if it is of benefit to pack the item or not
#         packOptionA = tbl[i - 1][p]
#         packOptionB = tbl[i - 1][p - profit] + weight

#         if (packOptionA == packOptionB):
#           tbl[i][p] = packOptionA
#           nsols[i][p] = nsols[i - 1][p] + nsols[i - 1][p - profit]
#         elif (packOptionA < packOptionB):
#           tbl[i][p] = packOptionA
#           nsols[i][p] = nsols[i - 1][p]
#         else:
#           tbl[i][p] = packOptionB
#           nsols[i][p] = nsols[i - 1][p - profit]

#   return DPSolution(kpi=kpi, capacity=capacity, profits_table=tbl, nsols_table=nsols)
