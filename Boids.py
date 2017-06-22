import itertools
from abc import abstractmethod, ABCMeta

import numpy as np

from Flock import Flock, Separate
from MathUtlis import pos_vector, vector2d
from Types import t_matcher
from strategy import WeighedRandom, Decision


class BaseAgent:
    vision = 2

    def __init__(self, space, x, y, r):
        super().__init__()
        self.r = r
        self.space = space
        self.pos = (x, y)

    def draw(self):
        pass


class AutonomicAgent(BaseAgent, metaclass=ABCMeta):
    def __init__(self, space, x, y, r, max_speed, max_energy=200):
        super().__init__(space, x, y, r)
        self.max_energy = max_energy
        self.energy = self.max_energy
        self.max_speed = max_speed
        self.heading = np.random.random(2)

        self.new_pos = self.pos
        self.new_heading = self.heading
        self.v_neighbors = []
        self.r_neighbors = []
        self.decision = Decision(None, None, None, None)

    def step(self):
        self.v_neighbors = self.space.get_neighbors(self.pos, BaseAgent.vision, include_center=False)
        self.decision = self.make_decision()
        self.heading = self.decision.update_heading(self.heading, self.v_neighbors)
        new_pos = self.decision.update_position(self.pos, self.heading)
        self.new_pos = self.space.torus_adj(new_pos)

    @abstractmethod
    def make_decision(self):
        pass

    def advance(self):
        self.r_neighbors = list(filter(lambda x: 2 * self.r >= self.space.get_distance(x.pos, self.new_pos),
                                       self.v_neighbors))
        if self.valid_decision():
            self.space.move_agent(self, self.new_pos)
        self.update_energy()

    def valid_decision(self):
        neighbors = filter(lambda x: not t_matcher(GrassAgent)(x), self.r_neighbors)
        return not colliding_decision(self, neighbors) and self.energy > 0

    def update_energy(self):
        self.energy -= self.decision.cost
        if self.energy < self.max_energy:
            self.eat()

    @abstractmethod
    def eat(self):
        pass


class MarkerAgent(BaseAgent):
    def __init__(self, space, x, y):
        super().__init__(space, x, y, r=0.02)

    def draw(self):
        return {'Color': 'black'}

    def step(self):
        pass

    def advance(self):
        pass


class GrassAgent(BaseAgent):
    def __init__(self, space, x, y, param):
        super().__init__(space, x, y, r=0.06)

    def draw(self):
        return {'Color': 'green'}

    def step(self):
        pass

    def advance(self):
        pass


class WolfAgent(AutonomicAgent):
    def __init__(self, space, x, y, param, max_speed=0.03):
        super().__init__(space, x, y, r=0.14, max_speed=max_speed)
        self.strategy = self.make_strategy(space)

    def make_strategy(self, space):
        hunger = Decision(hunger_value, 40, 0, eating(self, SheepAgent, space))
        coupling = Decision(coupling_value, 200, 0, Flock(self, space))

        return WeighedRandom([hunger, coupling])

    def draw(self):
        return {'Color': 'red', 'rs': BaseAgent.vision}

    def make_decision(self):
        return self.strategy(self)

    def eat(self):
        for sheep in filter(t_matcher(SheepAgent), self.r_neighbors):
            self.energy, sheep.energy = self.energy + sheep.energy, 0


class SheepAgent(AutonomicAgent):
    def __init__(self, space, x, y, param, max_speed=0.03):
        super().__init__(space, x, y, r=0.1, max_speed=max_speed)
        self.strategy = self.make_strategy(space)

    def make_strategy(self, space):
        hunger = Decision(hunger_value, 5, 0, eating(self, GrassAgent, space))
        fear = Decision(fear_value, 500, 0, escaping(self, space, aggressor_type=WolfAgent))
        coupling = Decision(coupling_value, 200, 0, Flock(self, space))

        return WeighedRandom([hunger, fear, coupling])

    def eat(self):
        if any(map(t_matcher(GrassAgent), self.r_neighbors)):
            self.energy += 10

    def draw(self):
        return {'Color': 'blue', 'rs': BaseAgent.vision}

    def make_decision(self):
        return self.strategy(self)


def threat_ratio(space, pos, neighbours):
    distances = map(space.get_distance,
                    itertools.repeat(pos),
                    map(pos_vector, neighbours))
    min_distance = min(distances, default=BaseAgent.vision)
    return (BaseAgent.vision - min_distance) / BaseAgent.vision


def coupling_value(agent):
    return threat_ratio(agent.space, agent.pos, filter(t_matcher(type(agent)), agent.v_neighbors))


def fear_value(agent):
    return threat_ratio(agent.space, agent.pos, filter(t_matcher(WolfAgent), agent.v_neighbors))


def hunger_value(agent):
    return max(0, agent.max_energy - agent.energy)


def colliding_decision(agent, neighbors):
    return any(filter(lambda x: x != agent, neighbors))


def escaping(agent, space, aggressor_type):
    separate = Separate(agent, space)

    def escape(neighbours):
        neighbours = filter(t_matcher(aggressor_type), neighbours)
        return separate(neighbours)

    return escape


def eating(me, food_type, space):
    def distance_to_me(x):
        distance = space.get_distance(me.pos, x)
        return distance

    def eating_(neighbours):
        neighbours = list(filter(t_matcher(food_type), neighbours))
        closest = min(map(pos_vector, neighbours),
                      key=distance_to_me,
                      default=me.pos)
        return vector2d(space)(me.pos, closest)

    return eating_
