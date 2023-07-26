from MOPSO import PSO
import subprocess
from utils import get_metrics
import numpy as np
import uproot
import argparse
import os

# parsing argument
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--continuing", type=int, action="store")
args = parser.parse_args()

# run pixel reconstruction and simple validation
def reco_and_validate(num_particles, iteration):
    if not os.path.exists("validation"):
        os.mkdir("validation")
    validation_result = "validation/iteration" + str(iteration) + ".root"
    subprocess.run(['cmsRun','reconstruction.py', "inputFiles=file:step2.root", "nEvents=100",
                     "parametersFile=parameters.csv", "outputFile=" + validation_result])
    with uproot.open(validation_result) as uproot_file:
        population_fitness = np.array([get_metrics(uproot_file, i) for i in range(num_particles)])
    return population_fitness

# define the lower and upper bounds
lb = [0.0, 0.0, 0.0, 0.0] #!!!
ub = [0.006, 0.03, 0.2, 1.0] #!!!
        
# create the PSO object
if not args.continuing:
    pso = PSO(fitness_function=reco_and_validate, lb=lb, ub=ub, num_particles=200, num_iterations=5, 
              num_objectives=2, w=0.5, c1=1, c2=1, max_iter_no_improv=None, tol=None)
else:
    pso = PSO(fitness_function=reco_and_validate, lb=lb, ub=ub)
    pso.load_checkpoint(args.continuing)

# run the optimization algorithm
pso.optimize()

