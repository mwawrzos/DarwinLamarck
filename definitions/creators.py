from deap import creator, base

creator.create('FitnessMax',
               base.Fitness,
               weights=(1., .1))

creator.create('Sheep',
               list,
               fitness=creator.FitnessMax)

creator.create('Wolf',
               list,
               fitness=creator.FitnessMax)
