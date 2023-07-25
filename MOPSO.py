import numpy as np
import subprocess
import os
from utils import get_metrics, write_csv, read_csv
import uproot
import json

class Particle:
    def __init__(self, lb=-10, ub=10, num_objectives=2, velocity=None, position=None, fitness=None, 
                 best_position=None, best_fitness=None):
        self.num_objectives = num_objectives
        if position is not None:
            self.velocity = velocity
            self.position = position
            self.fitness = fitness
            self.best_position = best_position
            self.best_fitness = best_fitness
        else:
            self.position = np.random.uniform(lb, ub)
            self.velocity = np.zeros_like(self.position)
            self.best_position = self.position
            self.best_fitness = np.ones(self.num_objectives) #inf for minimization
            self.fitness = np.ones(self.num_objectives)

    def update_velocity(self, global_best_position, w=0.5, c1=1, c2=1):
        r1 = np.random.uniform(0, 1)
        r2 = np.random.uniform(0, 1)
        cognitive = c1 * r1 * (self.best_position - self.position)
        social = c2 * r2 * (global_best_position - self.position)
        self.velocity = w * self.velocity + cognitive + social

    def update_position(self, lb, ub):
        self.position = np.clip(self.position + self.velocity, lb, ub)
    
    def evaluate_fitness(self, uproot_file, id):
        self.fitness = np.array(get_metrics(uproot_file, id))
        
        # sometimes tracks overflow happens which leads to perfect fitness but the result is actually bad
        if any(self.best_fitness == np.zeros(self.num_objectives)):
            self.fitness = np.ones(self.num_objectives)
            
        if all(self.fitness <= self.best_fitness):
            self.best_fitness = self.fitness
            self.best_position = self.position

class PSO:
    def __init__(self, lb, ub, num_objectives=2, num_particles=50, w=0.5, c1=1, c2=1, 
                 num_iterations=100, continuing=False, max_iter_no_improv=None, tol=None):
        if not continuing:
            saved_params = {
                "lb": lb,
                "ub": ub,
                "num_objectives": num_objectives,
                "num_particles": num_particles,
                "w": w,
                "c1": c1,
                "c2": c2,
                "max_iter_no_improv": max_iter_no_improv,
                "tol": tol,
            }
            with open('history/pso_saved_params.json', 'w') as f:
                json.dump(saved_params, f, indent=4)
        else:
            with open('history/pso_saved_params.json') as f:
                saved_params = json.load(f)
                
        self.lb = saved_params["lb"]
        self.ub = saved_params["ub"]
        self.num_objectives = saved_params["num_objectives"]
        self.num_particles = saved_params["num_particles"]
        self.w = saved_params["w"]
        self.c1 = saved_params["c1"]
        self.c2 = saved_params["c2"]
        self.max_iter_no_improv = saved_params["max_iter_no_improv"]
        self.tol = saved_params["tol"]
        
        if not continuing:
            self.num_iterations = num_iterations
            self.particles = [Particle(lb, ub, num_objectives=self.num_objectives) for _ in range(num_particles)]
            self.global_best_position = np.zeros_like(lb)
            self.global_best_fitness = np.ones(self.num_objectives)
            self.iteration = 0
        else:
            self.num_iterations = num_iterations
            num_params = len(self.lb)
            global_state = read_csv('history/global_state.csv')[0]
            self.global_best_position = np.array(global_state[:num_params], dtype=float)
            self.global_best_fitness = np.array(global_state[num_params:-1], dtype=float)
            self.iteration = int(global_state[-1])
            individual_states = read_csv('history/individual_states.csv')
            self.particles = [Particle(lb=self.lb,
                                       ub=self.ub, 
                                       num_objectives=self.num_objectives,
                                       position=np.array(individual_states[i][:num_params], dtype=float),
                                       velocity=np.array(individual_states[i][num_params:2*num_params], dtype=float),
                                       best_position=np.array(individual_states[i][2*num_params:3*num_params], dtype=float),
                                       best_fitness=np.array(individual_states[i][3*num_params:], dtype=float)
                                       ) for i in range(self.num_particles)]
        write_csv('parameters.csv', [particle.position for particle in self.particles])
            
    def optimize(self):
        uproot_file = None
        if not self.iteration:
            # clear old data, probably not the best way to do this
            os.system("rm -rf history/particles/*")
            os.system("rm -rf history/validation/*")
            
        for i in range(self.num_iterations):
            # run reconstruction and validate tracks
            validation_result = "history/validation/iteration" + str(self.iteration) + ".root"
            subprocess.run(['cmsRun','reconstruction.py', "inputFiles=file:full_validation/step2.root", 
                            "parametersFile=parameters.csv", "outputFile=" + validation_result])
            
            # evaluate fitness and update velocity
            for j, particle in enumerate(self.particles):
                uproot_file = uproot.open(validation_result)
                particle.evaluate_fitness(uproot_file, j)
                if all(particle.fitness <= self.global_best_fitness): 
                    self.global_best_fitness = particle.fitness
                    self.global_best_position = particle.position
                particle.update_velocity(self.global_best_position, self.w, self.c1, self.c2)
            uproot_file.close()
            
            # save position and fitness
            write_csv('history/particles/iteration' + str(self.iteration) + '.csv', 
                      [np.concatenate([particle.position, particle.fitness]) for particle in self.particles])

            # update positions
            for particle in self.particles:
                particle.update_position(self.lb, self.ub)
                
            # update input parameters for next iteration
            write_csv('parameters.csv', [particle.position for particle in self.particles])
            
            # save states of particles
            write_csv('history/individual_states.csv', 
                      [np.concatenate([particle.position, particle.velocity, particle.best_position, particle.best_fitness]) 
                       for particle in self.particles])

            # save global state
            self.iteration += 1
            write_csv('history/global_state.csv', 
                      [np.concatenate([self.global_best_position, self.global_best_fitness, [self.iteration]])])
        
        self.get_pareto_front()

    def get_pareto_front(self):
            pareto_front = []
            particles = np.concatenate([read_csv('history/particles/iteration' + str(i) + '.csv') 
                                    for i in range(self.iteration)])
            for particle in particles:
                dominated = False
                for other_particle in particles:
                    if all(particle[4:] == other_particle[4:]):
                        continue
                    if all(particle[4:] >= other_particle[4:]):
                        dominated = True
                        break
                if not dominated:
                    pareto_front.append(particle)
            write_csv('history/pareto_front.csv', pareto_front)
            return np.array(pareto_front)

    def calculate_crowding_distance(self, pareto_front):
        crowding_distances = {particle: 0 for particle in pareto_front}
        for objective_index in range(self.num_objectives):
            # Sort the Pareto front by the current objective function
            pareto_front_sorted = sorted(pareto_front, key=lambda x: x.fitness[objective_index])
            crowding_distances[pareto_front_sorted[0]] = np.inf
            crowding_distances[pareto_front_sorted[-1]] = np.inf
            for i in range(1, len(pareto_front_sorted)-1):
                crowding_distances[pareto_front_sorted[i]] += (
                    pareto_front_sorted[i+1].fitness[objective_index] -
                    pareto_front_sorted[i-1].fitness[objective_index]
                )
        return crowding_distances
