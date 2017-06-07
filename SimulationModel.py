import random

from mesa.datacollection import DataCollector
from mesa.model import Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation


def construct_agents(constructor, count, space, model):
    return [constructor(space,
                        model,
                        random.random() * space.x_max,
                        random.random() * space.y_max)
            for _ in range(count)]


def make_agents(x_max, y_max, agents, model):
    space = ContinuousSpace(x_max, y_max, True, grid_width=10, grid_height=10)

    res = []
    for agent_type, count in agents:
        res.extend(construct_agents(agent_type, count, space, model))

    return res


class SimulationModel(Model):
    def __init__(self, x_max, y_max, agents):
        super().__init__()

        self.schedule = SimultaneousActivation(self)
        for agent in make_agents(x_max, y_max, agents, self):
            self.schedule.add(agent)

        self.starved = 0

        self.data_collector = DataCollector(
            agent_reporters={'decision': lambda a: a.decision}
        )

    def step(self):
        self.schedule.step()
