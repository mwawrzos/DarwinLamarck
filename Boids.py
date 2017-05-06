import numpy as np

from Flocking import Flocking
from MathUtlis import neighbours_vectors, norm, sqr_dst
from Types import t_matcher


class BaseAgent:
    vision = 2

    def __init__(self, unique_id, space, x, y):
        super().__init__()
        self.unique_id = unique_id
        self.space = space
        self.pos = (x, y)
        self.space.place_agent(self, self.pos)

        self.decision = -1
        self.heading = None
        self.max_speed = None

    def draw(self):
        pass


class MarkerAgent(BaseAgent):
    def __init__(self, unique_id, space, x, y):
        super().__init__(unique_id, space, x, y)
        self.r = 0.02

    def draw(self):
        return {'Color': 'black'}

    def step(self):
        pass

    def advance(self):
        pass


class GrassAgent(BaseAgent):
    def __init__(self, unique_id, space, x, y):
        super().__init__(unique_id, space, x, y)
        self.r = 0.06

    def draw(self):
        return {'Color': 'green'}

    def step(self):
        pass

    def advance(self):
        pass


class WolfAgent(BaseAgent):
    def __init__(self, unique_id, space, x, y):
        super().__init__(unique_id, space, x, y)
        self.r = 0.14

    def draw(self):
        return {'Color': 'red', 'rs': BaseAgent.vision}

    def step(self):
        pass

    def advance(self):
        pass


class SheepAgent(BaseAgent):
    def __init__(self, unique_id, space, x, y, max_speed=0.03, heading=None):
        super().__init__(unique_id, space, x, y)
        self.max_speed = max_speed
        self.heading = heading if heading else np.random.random(2)
        self.asd = [i for (i, c) in enumerate([33, 22, 33]) for _ in range(c)]
        self.r = 0.1

        self.new_pos = None

    def draw(self):
        return {'Color': 'blue', 'rs': BaseAgent.vision}

    def step(self):
        self.update_heading(self.space.get_neighbors(self.pos, BaseAgent.vision, False))
        new_pos = np.array(self.pos) + self.heading * self.max_speed
        (new_x, new_y) = new_pos
        self.new_pos = self.space.torus_adj((new_x, new_y))

    def advance(self):
        if self.valid_decision():
            self.space.move_agent(self, self.new_pos)

    def update_heading(self, neighbours):
        new_heading = self.distributed_decision()(np.array(self.pos), neighbours)
        self.heading += norm(new_heading) * 0.3
        self.heading = norm(self.heading)

    def distributed_decision(self):
        self.decision = np.random.choice(self.asd)
        return decisions[self.decision]

    def valid_decision(self):
        neighbors = self.space.get_neighbors(self.new_pos, self.r * 2)
        neighbors = list(filter(t_matcher(SheepAgent), neighbors))
        neighbors.remove(self)
        return not neighbors


def eating(me, neighbours):
    neighbours = list(filter(t_matcher(GrassAgent), neighbours))
    if len(neighbours):
        return min(neighbours_vectors(me, neighbours),
                   key=sqr_dst)
    else:
        return np.array([0, 0])


def escaping(me, neighbours):
    neighbours = filter(t_matcher(WolfAgent), neighbours)
    return sum(neighbours_vectors(me, neighbours),
               np.array([0, 0]))


decisions = [Flocking(SheepAgent, 1.5), eating, escaping]
