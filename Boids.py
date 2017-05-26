from bisect import bisect_left
from math import sqrt

import numpy as np

from Flock import Flock
from MathUtlis import neighbours_vectors, norm, sqr_dst
from Types import t_matcher


class BaseAgent:
    vision = 2

    def __init__(self, unique_id, space, model, x, y, r):
        super().__init__()
        self.model = model
        self.r = r
        self.unique_id = unique_id
        self.space = space
        self.pos = (x, y)
        self.space.place_agent(self, self.pos)

        self.decision = -1
        self.heading = None
        self.max_speed = None

    def draw(self):
        pass


class AutonomicAgent(BaseAgent):
    def __init__(self, unique_id, space, model, x, y, r, max_speed, heading=None):
        super().__init__(unique_id, space, model, x, y, r)
        self.max_speed = max_speed
        self.heading = heading if heading else np.random.random(2)

        self.new_pos = None

    def step(self):
        self.update_heading(self.space.get_neighbors(self.pos, BaseAgent.vision, False))
        new_pos = np.array(self.pos) + self.heading * self.max_speed
        (new_x, new_y) = new_pos
        self.new_pos = self.space.torus_adj((new_x, new_y))

    def advance(self):
        if self.valid_decision():
            self.space.move_agent(self, self.new_pos)

    def valid_decision(self):
        return not colliding_decision(self)

    def update_heading(self, neighbours):
        # noinspection PyCallingNonCallable
        new_heading = self.distributed_decision()(np.array(self.pos), neighbours)
        self.heading += norm(new_heading) * 0.3
        self.heading = norm(self.heading)

    def distributed_decision(self):
        pass


class MarkerAgent(BaseAgent):
    def __init__(self, unique_id, space, model, x, y):
        super().__init__(unique_id, space, model, x, y, r=0.02)
        self.r = 0.02

    def draw(self):
        return {'Color': 'black'}

    def step(self):
        pass

    def advance(self):
        pass


class GrassAgent(BaseAgent):
    def __init__(self, unique_id, space, model, x, y):
        super().__init__(unique_id, space, model, x, y, r=0.06)
        self.r = 0.06

    def draw(self):
        return {'Color': 'green'}

    def step(self):
        pass

    def advance(self):
        pass


class WolfAgent(AutonomicAgent):
    def __init__(self, unique_id, space, model, x, y, max_speed=0.03, heading=None):
        super().__init__(unique_id, space, model, x, y, r=0.14, max_speed=max_speed, heading=heading)
        self.r = 0.14
        self.asd = [i for (i, c) in enumerate([1, 1]) for _ in range(c)]
        self.decisions = [Flock(WolfAgent), Eating(SheepAgent)]

    def draw(self):
        return {'Color': 'red', 'rs': BaseAgent.vision}

    def distributed_decision(self):
        self.decision = np.random.choice(self.asd)
        return self.decisions[self.decision]


class SheepAgent(AutonomicAgent):
    starved = 0

    def __init__(self, unique_id, space, model, x, y, max_speed=0.03, heading=None):
        super().__init__(unique_id, space, model, x, y, r=0.1, max_speed=max_speed, heading=heading)
        self.maxEnergy = 200
        self.asd = [i for (i, c) in enumerate([33, 22, 33]) for _ in range(c)]
        self.energy = self.maxEnergy

        self.decisions = [Eating(GrassAgent), escaping, Flock(SheepAgent)]

    def advance(self):
        super().advance()
        self.update_energy()
        if self.energy < 0:
            self.die()

    def update_energy(self):
        self.energy -= 1

        neighbors = self.space.get_neighbors(self.pos, self.r * 2)
        if any(map(t_matcher(GrassAgent), neighbors)):
            self.energy += 10
        self.energy = min(self.maxEnergy, self.energy)

    def draw(self):
        return {'Color': 'blue', 'rs': BaseAgent.vision}

    def distributed_decision(self):
        hunger = (self.maxEnergy - self.energy) * 5 + 0
        fear = self.fear() * 500 + 0
        coupling = 20
        decisions = [hunger,
                     hunger + fear,
                     hunger + fear + coupling]
        print(decisions)
        decision = np.random.rand() * decisions[-1]

        # self.decision = np.random.choice(self.asd)
        left = bisect_left(decisions, decision)
        return self.decisions[left]

    def die(self):
        # noinspection PyProtectedMember
        self.space._remove_agent(self.pos, self)
        self.model.schedule.remove(self)
        self.model.starved += 1

    def fear(self):
        neighbors = self.space.get_neighbors(self.pos, BaseAgent.vision, False)
        wolves = list(filter(t_matcher(WolfAgent), neighbors))
        distances = list(map(self.dst, wolves))
        vision_ = BaseAgent.vision - sqrt(min(distances, default=BaseAgent.vision * BaseAgent.vision))
        if vision_ < 0:
            print('dziwne', distances)
        return vision_ / BaseAgent.vision

    def dst(self, neighbour):
        x1, y1 = self.pos
        x2, y2 = neighbour.pos
        d_x = abs(x1 - x2)
        d_y = abs(y1 - y2)
        dx = min(d_x, self.space.width - d_x)
        dy = min(d_y, self.space.height - d_y)
        return dx * dx + dy * dy


def colliding_decision(agent):
    neighbours = agent.space.get_neighbors(agent.new_pos, agent.r * 2)
    neighbours = list(filter(t_matcher(type(agent)), neighbours))
    neighbours.remove(agent)
    return not not neighbours


def escaping(me, neighbours):
    neighbours = filter(t_matcher(WolfAgent), neighbours)
    return sum(neighbours_vectors(me, neighbours),
               np.array([0, 0]))


class Eating:
    def __init__(self, food_type):
        self.food_type = food_type

    def __call__(self, me, neighbours):
        neighbours = list(filter(t_matcher(self.food_type), neighbours))
        return -min(neighbours_vectors(me, neighbours),
                    key=sqr_dst,
                    default=np.array([0, 0]))
