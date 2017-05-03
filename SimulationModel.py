from mesa.datacollection import DataCollector
from mesa.model import Model
from mesa.time import SimultaneousActivation


class SimulationModel(Model):
    def __init__(self, agents):
        super().__init__()

        self.schedule = SimultaneousActivation(self)
        for agent in agents:
            self.schedule.add(agent)

        self.data_collector = DataCollector(
            agent_reporters={'decision': lambda a: a.decision}
        )

    def step(self):
        self.data_collector.collect(self)
        self.schedule.step()
