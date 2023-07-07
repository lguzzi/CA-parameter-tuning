import numpy as np
import subprocess
import os
from utils import get_metrics, write_csv, read_csv
import uproot
import json

class Particle:
    def __init__(self, lb=-10, ub=10, num_objectives=2, velocity=None, position=None, 
                 best_position=None, best_fitness=None):
        self.num_objectives = num_objectives
        if position is not None:
            self.velocity = velocity
            self.position = position
            self.fitness = None
            self.best_position = best_position
            self.best_fitness = best_fitness
        else:
            self.position = np.random.uniform(lb, ub)
            self.velocity = np.zeros_like(self.position)
            self.best_position = self.position
            self.best_fitness = np.ones(num_objectives) #inf for minimization
            self.fitness = np.ones(num_objectives)

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
        if self.best_fitness[0] == 0 or self.best_fitness[1] == 0:
            self.fitness = np.ones(self.num_objectives)
            
        if all(self.fitness < self.best_fitness):
            self.best_fitness = self.fitness
            self.best_position = self.position

class PSO:
    def __init__(self, lb, ub, num_objectives=2, num_particles=50, w=0.5, c1=1, c2=1, 
                 num_iterations=100, continuing=False, max_iter_no_improv=None, tol=None):
        if not continuing:
            self.lb = lb
            self.ub = ub
            self.num_objectives = num_objectives
            self.num_particles = num_particles
            self.w = w
            self.c1 = c1
            self.c2 = c2
            self.num_iterations = num_iterations
            self.max_iter_no_improv = max_iter_no_improv
            self.tol = tol
            self.particles = [Particle(lb, ub) for _ in range(num_particles)]
            self.global_best_position = np.zeros_like(lb)
            self.global_best_fitness = np.ones(num_objectives)
            self.iteration = 0
            write_csv('parameters.csv', [self.particles[i].position for i in range(self.num_particles)])
            saved_params = {
                "lb": self.lb,
                "ub": self.ub,
                "num_objectives": self.num_objectives,
                "num_particles": self.num_particles,
                "w": self.w,
                "c1": self.c1,
                "c2": self.c2,
                "max_iter_no_improv": self.max_iter_no_improv,
                "tol": self.tol,
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
            self.num_iterations = num_iterations
            self.max_iter_no_improv = max_iter_no_improv
            self.tol = saved_params["tol"]
            num_params = len(self.lb)
            global_state = read_csv('history/global_state.csv')[0]
            self.global_best_position = np.array(global_state[:num_params], dtype=float)
            self.global_best_fitness = np.array(global_state[num_params:-1], dtype=float)
            self.iteration = int(global_state[-1])
            individual_states = read_csv('history/individual_states.csv')
            self.particles = [Particle(
                                lb=self.lb, 
                                ub=self.ub, 
                                num_objectives=self.num_objectives,
                                position=np.array(individual_states[i][:num_params], dtype=float),
                                velocity=np.array(individual_states[i][num_params:2*num_params], dtype=float),
                                best_position=np.array(individual_states[i][2*num_params:3*num_params], dtype=float),
                                best_fitness=np.array(individual_states[i][3*num_params:], dtype=float)
                              ) for i in range(self.num_particles)]
            
    def optimize(self):
        uproot_file = None
        all_time_pareto_front = None
        # clear old data, probably not the best way to do this
        if not self.continuing:
            os.system("rm -rf history/parameters/*")
            os.system("rm -rf history/validation/*")
            os.system("rm -rf history/pareto_front/*")
            
        for i in range(self.num_iterations):
            # save tracking parameters
            write_csv('history/parameters/iteration' + str(self.iteration) + '.csv', 
                      [self.particles[i].position for i in range(self.num_particles)])
            
            # run reconstruction and validate tracks
            validation_result = "history/validation/iteration" + str(self.iteration) + ".root"
            subprocess.run(['cmsRun','reconstruction.py', "inputFiles=file:step2.root", 
                            "parametersFile=parameters.csv", "outputFile=" + validation_result])
            
            # evaluate fitness and update velocity
            for j, particle in enumerate(self.particles):
                uproot_file = uproot.open(validation_result)
                particle.evaluate_fitness(uproot_file, j)
                if all(particle.fitness < self.global_best_fitness): 
                    self.global_best_fitness = particle.fitness
                    self.global_best_position = particle.position
                particle.update_velocity(self.global_best_position, self.w, self.c1, self.c2)
            uproot_file.close()
                
            # save current pareto front
            pareto_front = self.get_pareto_front()
            write_csv('history/pareto_front/iteration' + str(self.iteration) + '.csv', 
                      [np.concatenate([pareto_front[i].position, pareto_front[i].fitness]) 
                       for i in range(len(pareto_front))])  
            
            # update all-time pareto front
            all_time_pareto_front = self.update_all_time_pareto_front(all_time_pareto_front, pareto_front)

            # update positions
            for j, particle in enumerate(self.particles):
                particle.update_position(self.lb, self.ub)
            write_csv('parameters.csv', [self.particles[i].position for i in range(self.num_particles)])
            
            # save states of particles
            write_csv('history/individual_states.csv', 
                      [np.concatenate([particle.position, particle.velocity, particle.best_position, particle.best_fitness]) 
                       for particle in self.particles])

            # save global state
            self.iteration += 1
            write_csv('history/global_state.csv', 
                      [np.concatenate([self.global_best_position, self.global_best_fitness, [self.iteration]])])
        
        write_csv('history/all_time_pareto_front.csv', 
            [np.concatenate([all_time_pareto_front[i].position, all_time_pareto_front[i].fitness]) 
             for i in range(len(all_time_pareto_front))]) 

    def get_pareto_front(self):
        pareto_front = []
        for particle in self.particles:
            dominated = False
            for other_particle in self.particles:
                if all(particle.fitness > other_particle.fitness):
                    dominated = True
                    break
            if not dominated:
                pareto_front.append(particle)
        # Sort the Pareto front by crowding distance
        # crowding_distances = self.calculate_crowding_distance(pareto_front)
        # pareto_front.sort(key=lambda x: crowding_distances[x], reverse=True)
        return pareto_front
    
    def update_all_time_pareto_front(self, all_time_pareto_front, pareto_front):
        if not all_time_pareto_front:
            return pareto_front
        
        pareto_front += all_time_pareto_front
        new_all_time_pareto_front = []
        for particle in pareto_front:
            dominated = False
            for other_particle in pareto_front:
                if all(particle.fitness > other_particle.fitness):
                    dominated = True
                    break
            if not dominated:
                new_all_time_pareto_front.append(particle)
        return new_all_time_pareto_front
        

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
