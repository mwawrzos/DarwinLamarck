import random


class Lamarck:
    def __init__(self, reward, penalty):
        self.reward = reward
        self.penalty = penalty

    def mut(self, decisions, decision):
        for i in range(len(decisions)):
            if i == decision:
                decisions[i].lamarck_mutation(random.gauss(self.reward, 1))
            else:
                decisions[i].lamarck_mutation(-random.gauss(self.penalty, 1))
