#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*******************************
despy.tests.test_abstract_types
*******************************
"""
import unittest

from despy.session import Session

class Test(unittest.TestCase):

    def testAbstractModel(self):
        session = Session.new()
        with self.assertRaises(TypeError):
            session.model = "Not an AbstractModel"

if __name__ == "__main__":
    unittest.main()