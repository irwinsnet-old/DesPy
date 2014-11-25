from despy.core.model import Model
from despy.core.simulation import Simulation

def is_model(obj):
    return isinstance(obj, Model)

def is_simulation(obj):
    return isinstance(obj, Simulation)
