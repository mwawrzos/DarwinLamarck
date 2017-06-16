import random

from mesa.datacollection import DataCollector
from mesa.model import Model
from mesa.space import ContinuousSpace
from mesa.time import SimultaneousActivation


def construct_agents(constructor, count, space):
    return [constructor(space,
                        random.random() * space.x_max,
                        random.random() * space.y_max,
                        [])
            for _ in range(count)]


def make_agents(agents, space):
    res = []
    for agent_type, count in agents:
        res.extend(construct_agents(agent_type, count, space))

    return res


class SimulationModel(Model):
    def __init__(self, x_max, y_max, agents):
        super().__init__()

        self.schedule = SimultaneousActivation(self)
        self.space = ContinuousSpace(x_max, y_max, True, grid_width=10, grid_height=10)
        for agent in make_agents(agents, self.space):
            self.schedule.add(agent)
        for agent in self.schedule.agents:
            self.space.place_agent(agent, agent.pos)

        self.starved = 0

        self.data_collector = DataCollector(
            agent_reporters={'decision': lambda a: a.decision}
        )

    def step(self):
        self.schedule.step()
        self.cleanup_corpses()

    def cleanup_corpses(self):
        for agent in self.schedule.agents:
            if agent.energy <= 0:
                self.starved += 1
                self.schedule.remove(agent)
                # noinspection PyProtectedMember
                self.space._remove_agent(agent.pos, agent)
