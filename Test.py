from Boids import SheepAgent, GrassAgent
from SimulationModel import SimulationModel

if __name__ == '__main__':

    model = SimulationModel(x_max=10,
                            y_max=10,
                            agents=[(GrassAgent, 100),
                                    (SheepAgent, 50)])
    for i in range(100):
        model.step()
