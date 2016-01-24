import despy as dp
import models.Ex2_1_model as ex2_1

mod = ex2_1.SingleChannelQueue()
sim = dp.Simulation(model = mod)
sim.config.reps = 2

sim.initialize()

sim.run(100)

results = sim.finalize()

print(results)