import random

from mesa.datacollection import DataCollector
from mesa.model import Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation


def construct_agents(constructor, fst_id, count, space):
    return [constructor(agent_id,
                        space,
                        random.random() * space.x_max,
                        random.random() * space.y_max)
            for agent_id in range(fst_id, count + fst_id)]


def make_agents(x_max, y_max, agents):
    space = ContinuousSpace(x_max, y_max, True, grid_width=10, grid_height=10)

    res = []
    agent_id = 0
    for agent_type, count in agents:
        res.extend(construct_agents(agent_type, agent_id, count, space))

    return res


class SimulationModel(Model):
    def __init__(self, x_max, y_max, agents):
        super().__init__()

        self.schedule = SimultaneousActivation(self)
        for agent in make_agents(x_max, y_max, agents):
            self.schedule.add(agent)

        self.data_collector = DataCollector(
            agent_reporters={'decision': lambda a: a.decision}
        )

    def step(self):
        self.data_collector.collect(self)
        self.schedule.step()
