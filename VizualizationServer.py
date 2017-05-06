from mesa.visualization.ModularVisualization import ModularServer

from Boids import GrassAgent, SheepAgent, WolfAgent
from Graphics import VerySimpleCanvas
from HistogramModule import HistogramModule
from SimulationModel import SimulationModel

agent_canvas = VerySimpleCanvas(lambda agent: agent.draw())

histogram = HistogramModule(list(range(4)), 200, 500)

server = ModularServer(SimulationModel,
                       [agent_canvas, histogram],
                       "Simulation",
                       x_max=10,
                       y_max=10,
                       agents=[(GrassAgent, 100),
                               (SheepAgent, 50),
                               (WolfAgent, 10)])
if __name__ == '__main__':
    server.launch()
