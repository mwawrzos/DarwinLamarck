from mesa.space import ContinuousSpace
from mesa.visualization.ModularVisualization import ModularServer

from HistogramModule import HistogramModule
from SimulationModel import SimulationModel
import random
from Boids import BaseAgent, GrassAgent, SheepAgent
from grphics import VerySimpleCanvas

agent_canvas = VerySimpleCanvas(BaseAgent.draw)


def construct_agents(constructor, fst_id, count, space):
    return [constructor(id,
                        space,
                        random.random() * space.x_max,
                        random.random() * space.y_max)
            for id in range(fst_id, count + fst_id)]


def make_agents(x_max, y_max):
    space = ContinuousSpace(x_max, y_max, True, grid_width=10, grid_height=10)
    agents = []
    agents.extend(construct_agents(GrassAgent, 0, 100, space))
    agents.extend(construct_agents(SheepAgent, 100, 50, space))
    return agents

histogram = HistogramModule(list(range(4)), 200, 500)

server = ModularServer(SimulationModel,
                       [agent_canvas, histogram],
                       "Simulation",
                       make_agents(10, 10))
if __name__ == '__main__':
    server.launch()
