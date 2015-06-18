#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*****************
despy.output.plot
*****************

:func:`Histogram`
"""

import math
import matplotlib.pyplot as plt
import numpy as np

def Histogram(data, folder, filename, title = None, x_label = None,
              y_label = None, bins = None):
    """Create a histogram and save it to the output folder.
    
    *Arguments*
        ``data`` A numpy array
    """
    plt.clf()
    
    #Convert data to a numpy array
    np_data = np.asanyarray(data, np.int32)

    # Calculate bin sizes if bins are not provided. Ensure bin edges are
    #   integer multiples.
    if bins is None:
        max_value = np.amax(np_data)
        min_value = np.amin(np_data)
        bin_size = math.ceil((max_value - min_value) / 10)
        bins = []
        bins.append(bin_size * math.floor(min_value / bin_size))
        while bins[-1] < max_value:
            bins.append(bins[-1] + bin_size)

    # Create Histogram
    plt.hist(np_data, bins)
    if title is not None:
        plt.title(title)
    if x_label is not None:
        plt.xlabel(x_label)
    if y_label is not None:
        plt.ylabel(y_label)
        
    # Save Histogram as file
    plt.savefig(folder + '/' + filename)
    
    
    
        