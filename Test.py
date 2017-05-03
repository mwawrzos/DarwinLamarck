from SimulationModel import SimulationModel
from VizualizationServer import make_agents

model = SimulationModel(make_agents(10, 10))
for i in range(100):
    model.step()
