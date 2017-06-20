import itertools
from bisect import bisect_left

import numpy as np

from Flock import Flock
from MathUtlis import norm, pos_vector, vector2d
from Types import t_matcher


class BaseAgent:
    vision = 2

    def __init__(self, space, x, y, r):
        super().__init__()
        self.r = r
        self.space = space
        self.pos = (x, y)

        self.decision = -1
        self.heading = None
        self.max_speed = None
        self.energy = 1
        self.max_energy = 1

    def draw(self):
        pass


class AutonomicAgent(BaseAgent):
    def __init__(self, space, x, y, r, max_speed, heading=None):
        super().__init__(space, x, y, r)
        self.max_speed = max_speed
        self.heading = heading if heading else np.random.random(2)

        self.new_pos = self.pos
        self.new_heading = self.heading
        self.v_neighbors = []
        self.r_neighbors = []

    def step(self):
        self.v_neighbors = self.space.get_neighbors(self.pos, BaseAgent.vision, include_center=False)
        self.r_neighbors = list(filter(lambda x: 2 * self.r >= self.space.get_distance(x.pos, self.new_pos),
                                       self.v_neighbors))
        self.update_heading(self.v_neighbors)
        new_pos = np.array(self.pos) + self.heading * self.max_speed
        (new_x, new_y) = new_pos
        self.new_pos = self.space.torus_adj((new_x, new_y))

    def advance(self):
        if self.valid_decision():
            self.space.move_agent(self, self.new_pos)

    def valid_decision(self):
        neighbors = filter(lambda x: not t_matcher(GrassAgent)(x), self.r_neighbors)
        return not colliding_decision(self, neighbors) and self.energy > 0

    def update_heading(self, neighbours):
        # noinspection PyCallingNonCallable
        self.new_heading = self.distributed_decision()(neighbours)
        self.heading += norm(self.new_heading) * 0.3
        self.heading = norm(self.heading)

    def distributed_decision(self):
        pass


class MarkerAgent(BaseAgent):
    def __init__(self, space, x, y):
        super().__init__(space, x, y, r=0.02)
        self.r = 0.02

    def draw(self):
        return {'Color': 'black'}

    def step(self):
        pass

    def advance(self):
        pass


class GrassAgent(BaseAgent):
    def __init__(self, space, x, y, param):
        super().__init__(space, x, y, r=0.06)
        self.r = 0.06

    def draw(self):
        return {'Color': 'green'}

    def step(self):
        pass

    def advance(self):
        pass


class WolfAgent(AutonomicAgent):
    def __init__(self, space, x, y, param, max_speed=0.03, heading=None):
        super().__init__(space, x, y, r=0.14, max_speed=max_speed, heading=heading)
        self.r = 0.14
        self.asd = [i for (i, c) in enumerate([1, 1]) for _ in range(c)]
        self.decisions = [Flock(self, WolfAgent, space), eating(self, SheepAgent, space)]
        self.max_energy = 200
        self.energy = self.max_energy

    def draw(self):
        return {'Color': 'red', 'rs': BaseAgent.vision}

    def distributed_decision(self):
        self.decision = np.random.choice(self.asd)
        return self.decisions[self.decision]

    def advance(self):
        super().advance()
        self.update_energy()

    def update_energy(self):
        self.energy -= 1
        if self.energy < self.max_energy:
            self.eat_sheep()

    def eat_sheep(self):
        for sheep in filter(t_matcher(SheepAgent), self.r_neighbors):
            self.energy, sheep.energy = self.energy + sheep.energy, 0


class SheepAgent(AutonomicAgent):
    starved = 0

    def __init__(self, space, x, y, param, max_speed=0.03, heading=None):
        super().__init__(space, x, y, r=0.1, max_speed=max_speed, heading=heading)
        self.max_energy = 200
        self.energy = self.max_energy

        self.decision = 0
        self.decisions = [eating(self, GrassAgent, space),
                          escaping(self, space),
                          Flock(self, SheepAgent, space)]

    def advance(self):
        super().advance()
        self.update_energy()

    def update_energy(self):
        self.energy -= 1
        if self.energy < self.max_energy:
            self.eat_grass()

    def eat_grass(self):
        if any(map(t_matcher(GrassAgent), self.r_neighbors)):
            self.energy += 10

    def draw(self):
        return {'Color': 'blue', 'rs': BaseAgent.vision}

    def distributed_decision(self):
        hunger = max(0, self.max_energy - self.energy) * 5 + 0
        fear = self.threat_ratio(filter(t_matcher(WolfAgent), self.v_neighbors)) * 500 + 0
        coupling = self.threat_ratio(filter(t_matcher(SheepAgent), self.v_neighbors)) * 200 + 1
        decisions = [hunger,
                     hunger + fear,
                     hunger + fear + coupling]
        decision = np.random.randint(decisions[-1] + 1)

        self.decision = bisect_left(decisions, decision)
        return self.decisions[self.decision]

    def threat_ratio(self, neighbours):
        distances = map(self.space.get_distance,
                        itertools.repeat(self.pos),
                        map(pos_vector, neighbours))
        min_distance = min(distances, default=BaseAgent.vision)
        return (BaseAgent.vision - min_distance) / BaseAgent.vision


def colliding_decision(agent, neighbors):
    return any(filter(lambda x: x != agent, neighbors))


def escaping(me, space):
    return Flock(me, WolfAgent, space, match_w=0, coherence_w=0)


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
