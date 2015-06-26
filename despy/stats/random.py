#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
from boto.rds import statusinfo
"""
******************
despy.stats.random
******************

:func:`Poisson`

**Python Library Dependencies**
    * :mod:
    
**External Library Dependencies**
    * :mod:
    * :mod:

..  todo

    Fix emperical so it will return more than one value.
    
    Extract check_shape feature to subroutine.
"""
import random as rnd
from enum import Enum
import scipy.stats as stats
import numpy as np


class errorCode(Enum):
    notSequence = 0
    invalidPMFProb = 1
    invalidPMFOrder = 2
    invalidPMFSum = 3
    invalidFinalProb = 4   

def Poisson(average, num=1):
    result = stats.poisson.rvs(average, size=num)
    if len(result) == 1:
        return np.asscalar(result)
    else:
        return result
        
class EmpericalGenerator(object):
    def __init__(self, pmf, cumulative = False):
        self.cumulative = cumulative
        total = 0
        for index in range(0, len(pmf)):
            if len(pmf[index]) < 2:
                raise StatsError(errorCode.notSequence)
            if not 0 < pmf[index][0] <= 1:
                    raise StatsError(errorCode.invalidPMFProb)
            if self.cumulative and index == (len(pmf) - 1):
                if pmf[-1][0] != 1:
                    raise StatsError(errorCode.invalidFinalProb)
            elif self.cumulative:
                if pmf[index][0] >= pmf[index+1][0]:
                    raise StatsError(errorCode.invalidPMFOrder)
            elif not self.cumulative:
                total += pmf[index][0]
        if not cumulative and total != 1:
            raise StatsError(errorCode.invalidPMFSum)
                
        self.pmf = pmf
        
    def get(self, num = 1):
        results = []
        for _ in range(0, num):
            rNum = rnd.random()
            limit = 0            
            for index in range(0, len(self.pmf)):
                if self.cumulative:
                    limit = self.pmf[index][0]
                else:
                    limit += self.pmf[index][0]
                if rNum < limit:
                    results.append(self.pmf[index][1])
                    break
        
        if len(results) == 1:
            return results[0]
        else:
            return results
        
class StatsError(Exception):
    def __init__(self, code):
        self.code = code   

    messages = [None for _ in range(len(errorCode))]

    messages[errorCode.notSequence.value] = \
        "Every PMF item must be sequence with at least two items."
    messages[errorCode.invalidPMFOrder.value] = \
        "Cumulative PMF probabilities must be ordered low to high."   
    messages[errorCode.invalidPMFProb.value] = \
        "PMF probability must be between 0 and 1."
    messages[errorCode.invalidPMFSum.value] = \
        "Non-cumulative PMF probabilities must sum to 1."
    messages[errorCode.invalidFinalProb.value] = \
        "Final cumulative PMF probability muse equal 1."
    
    @property
    def message(self):
        try:
            return self.messages[self.code]
        except IndexError:
            return "Invalid error code."
        
    def __str__(self):
        return self.message
    

        

            
        
    

            