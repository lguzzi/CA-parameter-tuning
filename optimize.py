from MOPSO import PSO

# define the lower and upper bounds
lb = [0.0, 0.0, 0.0, 0.0] #!!!
ub = [0.006, 0.03, 0.2, 1.0] #!!!

# create the PSO object
pso = PSO(lb=lb, ub=ub, num_particles=200, num_iterations=100, w=0.5, 
          c1=1, c2=1, max_iter_no_improv=None, tol=None)

# run the optimization algorithm
pso.optimize()

