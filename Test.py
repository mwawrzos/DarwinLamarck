from Boids import SheepAgent, GrassAgent, WolfAgent
from gen_model import SimulationModel

if __name__ == '__main__':
    grass_agent = GrassAgent, [[]] * 100
    sheep_agent = SheepAgent, [[]] * 50
    wolf_agent = WolfAgent, [[]] * 10

    model = SimulationModel(x_max=10,
                            y_max=10,
                            species=[grass_agent, sheep_agent, wolf_agent],
                            iterations=100)
    model.run_model()
