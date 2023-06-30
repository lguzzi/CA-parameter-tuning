import numpy as np
import matplotlib.pyplot as plt
from MOPSO import PSO
# the optimize function is wrong, the 1D does not work anymore, there is no test case so idk if the code works, 

def objective_function_1(x):
    return np.sin(x[0]) + np.sin(x[1])
    # return x**2


def objective_function_2(x):
    return np.cos(x[0])+np.cos(x[1])
    # return (x-2)**2


# define the lower and upper bounds
lb = [0.001, 0.001, 0.01, 0.01] #!!!
ub = [0.1, 0.1, 1.0, 1.0] #!!!

# create the PSO object
pso = PSO(objective_functions=[objective_function_1, objective_function_2], 
          lb=lb, ub=ub, num_particles=100, num_iterations=1, w=0.9, 
          c1=2, c2=2, max_iter_no_improv=None, tol=None)

# run the optimization algorithm
pareto_front = pso.optimize()

# print the results
print("Global best position:", pso.global_best_position)
print("Global best fitness:", pso.global_best_fitness)

# plot the Pareto front
pareto_x = [particle.fitness[0] for particle in pareto_front]
print(pareto_x)
pareto_y = [particle.fitness[1] for particle in pareto_front]
plt.scatter(pareto_x, pareto_y)
plt.xlabel("Objective 1")
plt.ylabel("Objective 2")
plt.title("Pareto Front")
plt.show()

# plot the convergence history
plt.plot(pso.history)
plt.xlabel("Iteration")
plt.ylabel("Global Best Fitness")
plt.title("Convergence History")
plt.show()
