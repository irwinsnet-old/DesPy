#!/usr/bin/env python3

import unittest
import itertools

import despy.core as dp
import scipy.stats as stats

class testResource(unittest.TestCase):
    def get_rnd_exp(self):
        return round(stats.expon.rvs(scale = 4))
    
    def test_resource_init(self):
        print()
        model = dp.Model("Resource Test #1")
        server = dp.Resource(model, "Server #1", 2)
        server.activity_time = self.get_rnd_exp
        self.assertEqual(server.name, "Server #1")
        ents = []
        for i in range(3):
            ents.append(dp.Entity(model, "Entity #{0}".format(i)))

        #   Verify resource has two positions with keys 1 and 2, and that both
        # are empty (i.e., contain None object).
        self.assertEqual(len(server._positions), 2)
        self.assertEqual(server.capacity, 2)
        self.assertTrue(1 in server._positions)
        self.assertTrue(2 in server._positions)
        self.assertFalse(0 in server._positions)
        self.assertFalse(3 in server._positions)
        
        self.assertTrue(server[1] is None)
        self.assertTrue(server[2] is None)
        
        #   Check that entities were created.
        self.assertEqual(ents[0].name, "Entity #0")
        self.assertEqual(ents[1].name, "Entity #1")
        
        #   Check get_empty_position()
        position = server.get_empty_position()
        self.assertEqual(position, 1)
        
        #   Check request(user)
        position = server.request(ents[0])
        self.assertEqual(position, 1)
        self.assertTrue(server[position] is not None)
        self.assertEqual(server[position].item_fld.name, "Entity #0")
        self.assertTrue(server[2] is None)

if __name__ == '__main__':
    unittest.main()

