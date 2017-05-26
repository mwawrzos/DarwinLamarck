from mesa.visualization.ModularVisualization import ModularServer

from Boids import GrassAgent, SheepAgent, WolfAgent
from Graphics import VerySimpleCanvas
from HistogramModule import HistogramModule
from SimulationModel import SimulationModel
from Text import VerySimpleText

agent_canvas = VerySimpleCanvas(lambda agent: agent.draw())

histogram = HistogramModule(list(range(4)), 200, 500, lambda sheep: sheep.decision)
histogram2 = HistogramModule(list(range(1, 202)), 200, 500, lambda sheep: sheep.energy)

server = ModularServer(SimulationModel,
                       [agent_canvas, histogram, histogram2, VerySimpleText()],
                       "Simulation",
                       x_max=10,
                       y_max=10,
                       agents=[(GrassAgent, 100),
                               (SheepAgent, 50),
                               (WolfAgent, 10)])
if __name__ == '__main__':
    server.launch()
