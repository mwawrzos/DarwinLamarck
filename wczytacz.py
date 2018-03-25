from gen import GenState
from visualization.VizualizationServer import *

s = GenState(1, 1, r'cp\17Sep13235554\039.pkl')
wolf_agent = WolfAgent, None, s.wolfs
sheep_agent = SheepAgent, None, s.sheep
server = ModularServer(SimulationModel,
                       [agent_canvas, histogram, histogram2, VerySimpleText()],
                       "Simulation",
                       {'x_max': 10,
                        'y_max': 10,
                        'species': [grass_agent, sheep_agent, wolf_agent],
                        'iterations': 2000})
server.launch()
