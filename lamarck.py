import random


class Lamarck:
    def __init__(self, reward, penalty, pb):
        self.reward = reward
        self.penalty = penalty
        self.pb = pb

    def mut(self, decisions, decision):
        for i in range(len(decisions)):
            if random.random() > self.pb:
                if i == decision:
                    decisions[i].lamarck_mutation(random.gauss(self.reward, 1))
                else:
                    decisions[i].lamarck_mutation(-random.gauss(self.penalty, 1))
