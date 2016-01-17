#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
************
tests.config
************

Provides standard configuration for automated tests.
"""

from despy.session import Config

def get_config():
    config = Config()
    config.write_files = False
    return config
