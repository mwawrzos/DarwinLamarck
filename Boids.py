import itertools
from abc import abstractmethod

import numpy as np

from Flock import Flock, Separate
from MathUtlis import pos_vector, vector2d
from Types import t_matcher
from strategy import WeighedRandom, Decision


class BaseAgent:
    vision = 2

    def __init__(self, space, x, y, r):
        self.r = r
        self.space = space
        self.pos = (x, y)

    def draw(self):
        pass


class AutonomicAgent(BaseAgent):
    def __init__(self, space, x, y, r, max_energy=200):
        super(AutonomicAgent, self).__init__(space, x, y, r)
        self.max_energy = max_energy
        self.energy = self.max_energy
        self.eaten = 0
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
        self.kill()

    @abstractmethod
    def eat(self):
        pass

    @abstractmethod
    def kill(self):
        pass


class MarkerAgent(BaseAgent):
    def __init__(self, space, x, y):
        super(MarkerAgent, self).__init__(space, x, y, r=0.02)

    def draw(self):
        return {'Color': 'black'}

    def step(self):
        pass

    def advance(self):
        pass


class GrassAgent(BaseAgent):
    def __init__(self, space, x, y, lamarck, param):
        super(GrassAgent, self).__init__(space, x, y, r=0.06)
        self.lamarck = lamarck
        self.param = param

    def draw(self):
        return {'Color': 'green'}

    def step(self):
        pass

    def advance(self):
        pass


class WolfAgent(AutonomicAgent):
    def __init__(self, space, x, y, lamarck, param):
        super(WolfAgent, self).__init__(space, x, y, r=0.14)
        self.max_energy = 100
        self.strategy = self.make_strategy(space, lamarck, param)

    def make_strategy(self, space, lamarck, param):
        hunger = make_wolf_hunger(self, space, *param[0:3])
        coupling = make_coupling(self, space, *param[3:5])

        return WeighedRandom(lamarck, [hunger, coupling])

    def draw(self):
        return {'Color': 'red', 'rs': BaseAgent.vision}

    def make_decision(self):
        return self.strategy(self)

    def eat(self):
        for sheep in filter(t_matcher(SheepAgent), self.r_neighbors):
            self.energy, sheep.energy = self.energy + 400, 0
            self.eaten += 1

    def kill(self):
        for sheep in filter(t_matcher(SheepAgent), self.r_neighbors):
            sheep.energy = 0
            self.eaten -= 1

    def get_params(self):
        d = self.strategy.decisions
        return [d[0].a, d[0].b, d[0].speed_weight, d[1].a, d[1].b]


class SheepAgent(AutonomicAgent):
    def kill(self):
        pass

    def __init__(self, space, x, y, lamarck, param):
        super(SheepAgent, self).__init__(space, x, y, r=0.1)
        self.strategy = self.make_strategy(space, lamarck, param)

    def make_strategy(self, space, lamarck, param):
        hunger = make_sheep_hunger(self, space, *param[0:2])
        fear = make_fear(self, space, *param[2:5])
        coupling = make_coupling(self, space, *param[5:7])

        return WeighedRandom(lamarck, [hunger, fear, coupling])

    def eat(self):
        if any(map(t_matcher(GrassAgent), self.r_neighbors)):
            self.energy += 10
            self.eaten += 1

    def draw(self):
        return {'Color': 'blue', 'rs': BaseAgent.vision}

    def make_decision(self):
        return self.strategy(self)

    def get_params(self):
        d = self.strategy.decisions
        return [d[0].a, d[0].b, d[1].a, d[1].b, d[1].speed_weight, d[2].a, d[2].b]


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


def make_wolf_hunger(agent, space, hunger_a, hunger_b, hunger_speed):
    hunger = Decision(hunger_value, hunger_a, hunger_b,
                      eating(agent, SheepAgent, space),
                      speed_weight=hunger_speed)
    return hunger


def make_sheep_hunger(agent, space, hunger_a, hunger_b):
    hunger = Decision(hunger_value, hunger_a, hunger_b,
                      eating(agent, GrassAgent, space))
    return hunger


def make_fear(agent, space, fear_a, fear_b, fear_speed):
    fear = Decision(fear_value, fear_a, fear_b,
                    escaping(agent, space, aggressor_type=WolfAgent),
                    speed_weight=fear_speed)
    return fear


def make_coupling(agent, space, coupling_a, coupling_b):
    return Decision(coupling_value,
                    coupling_a,
                    coupling_b,
                    Flock(agent, space))
