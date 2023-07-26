import numpy as np
import os
from utils import write_csv, read_csv
import json

class Particle:
    def __init__(self, lb=-10, ub=10, num_objectives=2):
        self.num_objectives = num_objectives
        self.position = np.random.uniform(lb, ub)
        self.velocity = np.zeros_like(self.position)
        self.best_position = self.position
        self.best_fitness = np.array([np.inf] * self.num_objectives) #inf for minimization
        self.fitness = np.array([np.inf] * self.num_objectives)
    
    def set_state(self, velocity, position, best_position, best_fitness):
        self.velocity = velocity
        self.position = position
        self.best_position = best_position
        self.best_fitness = best_fitness

    def update_velocity(self, global_best_position, w=0.5, c1=1, c2=1):
        r1 = np.random.uniform(0, 1)
        r2 = np.random.uniform(0, 1)
        cognitive = c1 * r1 * (self.best_position - self.position)
        social = c2 * r2 * (global_best_position - self.position)
        self.velocity = w * self.velocity + cognitive + social

    def update_position(self, lb, ub):
        self.position = np.clip(self.position + self.velocity, lb, ub)
    
    def evaluate_fitness(self, new_fitness):
        self.fitness = new_fitness
        if np.all(self.fitness <= self.best_fitness):
            self.best_fitness = self.fitness
            self.best_position = self.position

class PSO:
    def __init__(self, fitness_function, lb, ub, num_objectives=2, num_particles=50, w=0.5, c1=1, c2=1, 
                 num_iterations=100, max_iter_no_improv=None, tol=None):
        self.fitness_function = fitness_function    
        self.lb = lb
        self.ub = ub
        self.num_objectives = num_objectives
        self.num_particles = num_particles
        self.num_params = len(ub)
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.num_iterations = num_iterations
        self.max_iter_no_improv = max_iter_no_improv
        self.tol = tol
        self.particles = [Particle(lb, ub, num_objectives=self.num_objectives) for _ in range(num_particles)]
        self.global_best_position = np.zeros(self.num_params)
        self.global_best_fitness = np.array([np.inf] * self.num_objectives)
        self.iteration = 0
        
    def load_checkpoint(self, num_additional_iterations):
        with open('checkpoint/pso_params.json') as f:
            pso_params = json.load(f)
        global_state = read_csv('checkpoint/global_state.csv')[0]
        individual_states = read_csv('checkpoint/individual_states.csv')
        self.lb = pso_params["lb"]
        self.ub = pso_params["ub"]
        self.num_objectives = pso_params["num_objectives"]
        self.num_particles = pso_params["num_particles"]
        self.num_params = pso_params["num_params"]
        self.w = pso_params["w"]
        self.c1 = pso_params["c1"]
        self.c2 = pso_params["c2"]
        self.max_iter_no_improv = pso_params["max_iter_no_improv"]
        self.tol = pso_params["tol"]
        self.num_iterations = num_additional_iterations
        self.iteration = num_additional_iterations
        self.global_best_position = np.array(global_state[:self.num_params], dtype=float)
        self.global_best_fitness = np.array(global_state[self.num_params:-1], dtype=float)
        self.iteration = int(global_state[-1])
        self.particles = [Particle(self.lb, self.ub, num_objectives=self.num_objectives) for _ in range(self.num_particles)]
        for i, particle in enumerate(self.particles):
            particle.set_state(
                position=np.array(individual_states[i][:self.num_params], dtype=float),
                velocity=np.array(individual_states[i][self.num_params:2*self.num_params], dtype=float),
                best_position=np.array(individual_states[i][2*self.num_params:3*self.num_params], dtype=float),
                best_fitness=np.array(individual_states[i][3*self.num_params:], dtype=float)
            )
            
    def optimize(self):
        # create folders to save history and checkpoint
        if not os.path.exists("history"):
            os.mkdir("history")
            
        if not os.path.exists("checkpoint"):
            os.mkdir("checkpoint")
            
        # clear old data, probably not the best way to do this
        if not self.iteration:
            os.system("rm -rf checkpoint/*")
            os.system("rm -rf history/*")            

        # save pso params
        pso_params = {
            "lb": self.lb,
            "ub": self.ub,
            "num_objectives": self.num_objectives,
            "num_particles": self.num_particles,
            "num_params": self.num_params,
            "w": self.w,
            "c1": self.c1,
            "c2": self.c2,
            "max_iter_no_improv": self.max_iter_no_improv,
            "tol": self.tol,
        }
        with open('checkpoint/pso_params.json', 'w') as f:
            json.dump(pso_params, f, indent=4)
        
        # main pso loop
        for _ in range(self.num_iterations):
            # params for current iteration
            write_csv('parameters.csv', [particle.position for particle in self.particles])
            
            # calculate fitness for all particles
            population_fitness = self.fitness_function(self.num_particles, self.iteration)
            
            # evaluate fitness and update velocity
            for j, particle in enumerate(self.particles):
                particle.evaluate_fitness(population_fitness[j])
                if all(particle.fitness <= self.global_best_fitness): 
                    self.global_best_fitness = particle.fitness
                    self.global_best_position = particle.position
                particle.update_velocity(self.global_best_position, self.w, self.c1, self.c2)
            
            # save position and fitness
            write_csv('history/iteration' + str(self.iteration) + '.csv', 
                      [np.concatenate([particle.position, particle.fitness]) for particle in self.particles])

            # update positions
            for particle in self.particles:
                particle.update_position(self.lb, self.ub)
            
            # save current states of particles
            write_csv('checkpoint/individual_states.csv', 
                      [np.concatenate([particle.position, particle.velocity, particle.best_position, particle.best_fitness]) 
                       for particle in self.particles])

            # save global state
            self.iteration += 1
            write_csv('checkpoint/global_state.csv', 
                      [np.concatenate([self.global_best_position, self.global_best_fitness, [self.iteration]])])
        
        self.get_pareto_front()

    def get_pareto_front(self):
        pareto_front = []
        particles = np.concatenate([read_csv('history/iteration' + str(i) + '.csv') 
                                for i in range(self.iteration - self.num_iterations, self.iteration)])
        
        if os.path.exists("checkpoint/pareto_front.csv"):
            particles = np.concatenate([particles, read_csv("checkpoint/pareto_front.csv")])
            
        for particle in particles:
            dominated = False
            for other_particle in particles:
                if np.all(particle[self.num_params:] == other_particle[self.num_params:]):
                    continue
                if np.all(particle[self.num_params:] >= other_particle[self.num_params:]):
                    dominated = True
                    break
            if not dominated:
                pareto_front.append(particle)
                
        write_csv('checkpoint/pareto_front.csv', pareto_front)
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
