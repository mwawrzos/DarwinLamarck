from mesa.visualization.ModularVisualization import ModularServer

from Boids import GrassAgent, SheepAgent, WolfAgent
from Text import VerySimpleText
from gen_model import SimulationModel
from visualization.Graphics import VerySimpleCanvas
from visualization.HistogramModule import HistogramModule

agent_canvas = VerySimpleCanvas(lambda agent: agent.draw())

histogram = HistogramModule(list(range(4)), 200, 500, lambda sheep: sheep.strategy.decision)
histogram2 = HistogramModule(list(range(1, 202)), 200, 500, lambda sheep: sheep.energy)

grass_agent = GrassAgent, False, [[]] * 100
sheep_agent = SheepAgent, True, [[5, 0, 500, 500, 0, 200, 0]] * 50
wolf_agent = WolfAgent, False, [[40, 0, 500, 200, 20]] * 10
server = ModularServer(SimulationModel,
                       [agent_canvas, histogram, histogram2, VerySimpleText()],
                       "Simulation",
                       {'x_max': 10,
                        'y_max': 10,
                        'species': [grass_agent, sheep_agent, wolf_agent],
                        'iterations': 2000})
if __name__ == '__main__':
    server.launch()
