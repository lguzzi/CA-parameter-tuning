import numpy as np
import matplotlib.pyplot as plt
from MOPSO import PSO

# define the lower and upper bounds
lb = [0.0, 0.0, 0.0, 0.2] #!!!
ub = [0.006, 0.03, 0.2, 0.8] #!!!

# create the PSO object
pso = PSO(lb=lb, ub=ub, num_particles=200, num_iterations=3, w=0.5, 
          c1=1, c2=1, max_iter_no_improv=None, tol=None)

# run the optimization algorithm
pso.optimize()

