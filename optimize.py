from MOPSO import PSO
import subprocess
from utils import get_metrics, write_csv
import numpy as np
import uproot
import argparse
import os

# parsing argument
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--continuing", type=int, action="store")
args = parser.parse_args()

# run pixel reconstruction and simple validation
def reco_and_validate(params):
    if not os.path.exists("temp"):
        os.mkdir("temp")
    write_csv("temp/parameters.csv", params)
    validation_result = "temp/simple_validation.root"
    subprocess.run(['cmsRun','reconstruction.py', "inputFile=file:input/step2.root", "nEvents=1000",
                     "parametersFile=temp/parameters.csv", "outputFile=" + validation_result])
    num_particles = len(params)
    with uproot.open(validation_result) as uproot_file:
        population_fitness = np.array([get_metrics(uproot_file, i) for i in range(num_particles)])
    return population_fitness

# get default metrics
default_params = [[0.0020000000949949026, 0.003000000026077032, 0.15000000596046448, 0.25]]
default_metrics = reco_and_validate(default_params)
write_csv("default.csv", [np.concatenate([default_params[0], default_metrics[0]])])

# define the lower and upper bounds
lb = [0.0, 0.0, 0.0, 0.0] #!!!
ub = [0.006, 0.03, 0.2, 1.0] #!!!
        
# create the PSO object
if not args.continuing:
    pso = PSO(objectives_function=reco_and_validate, lb=lb, ub=ub, num_particles=200, num_iterations=25, 
              num_objectives=2, w=0.5, c1=1, c2=1, max_iter_no_improv=None, tol=None)
else:
    pso = PSO(objectives_function=reco_and_validate, lb=lb, ub=ub)
    pso.load_checkpoint(args.continuing)

# run the optimization algorithm
pso.optimize()

