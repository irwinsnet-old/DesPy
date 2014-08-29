#!/usr/bin/env python3
""""A two server queueing model."""

##TODO: Add process that generates customers.

from despyb import Environment, Model, Process, Entity, Event

class AbelBakerModel(Model):
    def initialize(self):
        pass
    
    def __init__(self, env):
        Model.__init__(self, "Abel Baker Model", env)
        self.initialize()
    
class Customer(Entity):
    def __init(self, number, model):
        Entity("Customer", number, model)

class CustomerArrival(Event):
    def __init__(self, customer, model):
        self._customer = customer
        Event.__init__(self, "Customer Arrival", model)

class CustomerGenerator(Process):
    def _generator(self):
        customerNumber = 1
        interArrivalTime = 3
        firstCustomer = Customer(1, self.model)
        yield self.scheduleProcessPreEvent(
                CustomerArrival(firstCustomer, self.model), interArrivalTime)
        
        #while customerNumber < 20:
        #    cust = Customer("Customer", customerNumber, self.model)
        #    yield Event("Customer Arrival")

def main():
    env = Environment()
    
    abModel = AbelBakerModel(env)
    cg = CustomerGenerator("Customer Generator", abModel)
    arrivalEvent = cg.get_next_event()
    print(arrivalEvent.name)
    
if __name__ == '__main__':
    main()
