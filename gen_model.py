import random

from mesa import Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation

from Boids import AutonomicAgent
from Types import t_matcher


class SimulationModel(Model):
    def __init__(self, x_max, y_max, species, iterations):
        super(SimulationModel, self).__init__()

        self.starved = 0
        self.space = ContinuousSpace(x_max, y_max,
                                     grid_width=10, grid_height=10,
                                     torus=True)
        self.schedule = SimultaneousActivation(self)

        self.iterations = iterations

        self.species = []
        self.create_population(species)

    def create_population(self, species):
        for specie, params in species:
            individuals = []
            for param in params:
                individuals.append(self.create_individual(specie, param))
                self.schedule.add(individuals[-1])
            self.species.append(individuals)

    def create_individual(self, specie, param):
        x = random.random() * self.space.x_max
        y = random.random() * self.space.y_max
        ind = specie(self.space, x, y, param)
        self.space.place_agent(ind, ind.pos)
        return ind

    def step(self):
        self.schedule.step()
        self.cleanup_corpses()
        self.update_iterations()

    def update_iterations(self):
        self.iterations -= 1
        if not self.iterations:
            self.running = False

    def cleanup_corpses(self):
        for agent in filter(t_matcher(AutonomicAgent), self.schedule.agents):
            if agent.energy <= 0:
                self.schedule.remove(agent)
                # noinspection PyProtectedMember
                self.space._remove_agent(agent.pos, agent)
                self.starved += 1

    def results(self):
        def get_energy(individual):
            return individual.eaten, individual.energy

        def get_energies(specie):
            return map(get_energy, specie)

        return map(get_energies, self.species)
