from gen import GenState
from visualization.VizualizationServer import *

s = GenState(r'cp\darwin_owce_wilki_3030\019.pkl')
wolf_agent = WolfAgent, s.wolfs
sheep_agent = SheepAgent, s.sheep
server = ModularServer(SimulationModel,
                       [agent_canvas, histogram, histogram2, VerySimpleText()],
                       "Simulation",
                       x_max=10,
                       y_max=10,
                       species=[grass_agent, sheep_agent, wolf_agent],
                       iterations=2000)
server.launch()
