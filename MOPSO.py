import numpy as np
import csv
import subprocess
import uproot

class Particle:
    def __init__(self, lb=-10, ub=10, num_objectives=2):
        self.position = np.random.uniform(lb, ub)
        self.velocity = np.zeros_like(self.position)
        self.best_position = self.position
        self.best_fitness = [np.inf] * num_objectives #inf for minimization
        self.fitness = [np.inf] * num_objectives

    def update_velocity(self, global_best_position, w=0.5, c1=1, c2=1):
        r1 = np.random.uniform(0, 1)
        r2 = np.random.uniform(0, 1)
        cognitive = c1 * r1 * (self.best_position - self.position)
        social = c2 * r2 * (global_best_position - self.position)
        self.velocity = w * self.velocity + cognitive + social

    def update_position(self, lb, ub):
        self.position = np.clip(self.position + self.velocity, lb, ub)

    # def evaluate_fitness(self, objective_functions):
    #     self.fitness = np.array([obj_func(self.position) for obj_func in objective_functions])
    #     if any(self.fitness < self.best_fitness):
    #         self.best_fitness = self.fitness
    #         self.best_position = self.position
    
    def evaluate_fitness(self, filename, id):
        with uproot.open(filename) as output:
            out = output['simpleValidation' + str(id)]['output']
            totalRec = out['rt'].array()[0]
            totalAss = out['at'].array()[0]
            totalSim = out['st'].array()[0]
            
        self.fitness = np.array([totalSim / totalAss, (totalRec - totalAss) / totalRec])
        
        if any(self.fitness < self.best_fitness):
            self.best_fitness = self.fitness
            self.best_position = self.position

class PSO:
    def __init__(self, objective_functions, lb, ub, num_particles=50, w=0.5, c1=1, c2=1, num_iterations=100, max_iter_no_improv=None, tol=None):
        self.objective_functions = objective_functions
        self.num_particles = num_particles
        self.lb = lb
        self.ub = ub
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.num_iterations = num_iterations
        self.max_iter_no_improv = max_iter_no_improv
        self.tol = tol

        self.particles = [Particle(lb, ub) for _ in range(num_particles)]
        self.global_best_position = np.zeros_like(lb)
        self.global_best_fitness = [np.inf, np.inf] #TODO: you can improve it to be a list of size num_objectives
        self.history = []
        self.write_params('parameters.csv')
            
    def write_params(self, filename):
        with open(filename, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            for i in range(self.num_particles):
                writer.writerow(self.particles[i].position)     

    def optimize(self):
        for i in range(self.num_iterations):
            subprocess.run(['cmsRun','reconstruction.py', "outputFileName=" + "output/output" + str(i) + ".root"])
            for j, particle in enumerate(self.particles):
                particle.evaluate_fitness("output/output" + str(i) + ".root", j)

                if all(particle.fitness < self.global_best_fitness): 
                    self.global_best_fitness = particle.fitness
                    self.global_best_position = particle.position

                self.update_particle_best(particle)
                self.update_global_best()

                particle.update_velocity(
                    self.global_best_position, self.w, self.c1, self.c2)
                particle.update_position(self.lb, self.ub)

            self.write_params('parameters.csv')
            self.write_params('params/parameters' + str(i) + '.csv')
            self.history.append(self.global_best_fitness)

        pareto_front = self.get_pareto_front()
        return pareto_front

    def update_particle_best(self, particle):
        if any(particle.fitness < particle.best_fitness):
            particle.best_fitness = particle.fitness
            particle.best_position = particle.position

    def update_global_best(self):
        for particle in self.particles:
            if all(particle.fitness <= self.global_best_fitness):
                self.global_best_fitness = particle.fitness
                self.global_best_position = particle.position

    def get_pareto_front(self):
        pareto_front = []
        for particle in self.particles:
            dominated = False
            for other_particle in self.particles:
                if all(particle.fitness >= other_particle.fitness) and any(particle.fitness > other_particle.fitness):
                    dominated = True
                    break
            if not dominated:
                pareto_front.append(particle)
        # Sort the Pareto front by crowding distance
        crowding_distances = self.calculate_crowding_distance(pareto_front)
        pareto_front.sort(key=lambda x: crowding_distances[x], reverse=True)
        return pareto_front

    def calculate_crowding_distance(self, pareto_front):
        num_objectives = len(self.objective_functions)
        crowding_distances = {particle: 0 for particle in pareto_front}
        for objective_index in range(num_objectives):
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








