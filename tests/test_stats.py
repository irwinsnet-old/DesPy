
import unittest

import despy.stats.random as dsr
import numpy as np

class testRandom(unittest.TestCase):
    
    def test_Poisson(self):
        print()
        print("===== Poisson Test=====")
        # Get a single Poisson random number
        avg = 28
        result = dsr.Poisson(avg)
        self.assertIsInstance(result, int)
        print("Poisson Random Number: {0}".format(result))
        
        # Get several random numbers
        numInts = 10
        result2 = dsr.Poisson(avg, num=numInts)
        self.assertEqual(len(result2), numInts)
        print("{0} Poisson Random Numbers: {1}".format(numInts,
                                                       result2))
        print("Average of random numbers: {0}".format( \
                                                np.average(result2)))

    def test_Emperical(self):
        print()
        print("===== Emperical Non Cumulative Test=====")
        
        #Test returns number 1 through 4.
        pmf = [(0.25, 1), (0.4, 2), (0.2, 3), (0.15, 4)]
        emp_gen = dsr.EmpericalGenerator(pmf)
        result = emp_gen.get()
        print("Emperical Random Value: {0}".format(result))
        self.assertIn(result, [1, 2, 3, 4])
        
        #Test returns a list.
        numInts = 20
        results = emp_gen.get(numInts)
        print("{0} Random Values: {1}".format(numInts, results))
        self.assertEqual(len(results), numInts)
        for n in range(0, numInts):
            self.assertIn(results[n], [1, 2, 3, 4])
            
        print()
        print("===== Emperical Cumulative Test=====")
        
        #Test returns number 1 through 4.
        pmf2 = [(0.25, 1), (0.65, 2), (0.85, 3), (1, 4)]
        emp_gen = dsr.EmpericalGenerator(pmf2, True)
        result = emp_gen.get()
        print("Emperical Random Value: {0}".format(result))
        self.assertIn(result, [1, 2, 3, 4])
        
        #Test returns a list.
        numInts = 20
        results = emp_gen.get(numInts)
        print("{0} Random Values: {1}".format(numInts, results))
        self.assertEqual(len(results), numInts)
        for n in range(0, numInts):
            self.assertIn(results[n], [1, 2, 3, 4])
            
        #Verify incorrect pmf parameters throw errors.
        pmf3 = [(0.25, 1), (0.4, 2), (0.2, 3)]
        with self.assertRaises(dsr.StatsError) as cm:
            _ = dsr.EmpericalGenerator(pmf3)
        self.assertEqual(cm.exception.code, dsr.errorCode.invalidPMFSum)
        
        pmf4 = [(0.25, 1), (0.4,), (0.2, 3), (0.15, 4)]
        with self.assertRaises(dsr.StatsError) as cm:
            _ = dsr.EmpericalGenerator(pmf4)
        self.assertEqual(cm.exception.code, dsr.errorCode.notSequence)
        
        pmf5 = [(0.25, 1), (0.85, 2), (0.65, 3), (1.00, 4)]
        with self.assertRaises(dsr.StatsError) as cm:
            _ = dsr.EmpericalGenerator(pmf5, True)
        code = cm.exception.code
        self.assertEqual(code, dsr.errorCode.invalidPMFOrder)
        
        pmf6 = [(0.25, 1), (0.65, 2), (0.85, 3), (0.95, 4)]
        with self.assertRaises(dsr.StatsError) as cm:
            _ = dsr.EmpericalGenerator(pmf6, True)
        code = cm.exception.code
        self.assertEqual(code, dsr.errorCode.invalidFinalProb)
            
        