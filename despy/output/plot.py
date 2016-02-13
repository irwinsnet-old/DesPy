#   Despy: A discrete event simulation framework for Python
#   Version 0.1
#   Released under the MIT License (MIT)
#   Copyright (c) 2015, Stacy Irwin
"""
*****************
despy.output.plot
*****************

..  autosummary::

    Histogram

**Python Library Dependencies**
    * :mod:`math`
    
**External Library Dependencies**
    * :mod:`numpy`
    * :mod:`matplotlib.pyplot`

..  todo

    Add a filetype parameter to allow file types other than png.
    
    Add default filetype to generator object.
"""

import math

import matplotlib.pyplot as plt
import numpy as np

def BarPlot(data, xlabel, ylabel, title='Counts', width=0.2, color='g'):
    plt.clf()
    x_vals = range(len(data))
    plt.bar(x_vals, data, width, color=color, align='center')
    plt.xticks(x_vals, ["{}".format(x) for x in x_vals])
    plt.title
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.show()
    return plt.gcf()

class Histo():
    def __init__(self, data):
        self._data = data        
        self._figure = plt.figure()
        self._ax = self._figure.add_subplot(111)
        
    @property
    def figure(self):
        return self._figure
    
    @property
    def data(self):
        return self._data

def Histogram(data, folder, filename, title = None, x_label = None,
              y_label = None, bins = None):
    """Create a histogram and save it to the output folder.
    
    As of version 0.1, despy is using the default configuration of
    the Matplotlib, with the Qt4Agg backend. Qt4Agg supports the
    following file extensions (i.e., image formats): eps, pdf, pgf, png,
    ps, raw, rgba, svg, svgz. However despy will generate png files so
    they will be visible in simple HTML documents.
    
    *Arguments*
        ``data``
            A list of 32-bit integers (-2147483648 to 2147483647). Can
            also be a numpy array, or any Python array-like object.
        ``folder`` String
            The full path to the folder where the histogram image file
            will be saved.
        ``filename`` (tring
            The png fill will be assigned this file name, which should
            contain a ".png" file type extension.
        ``title`` String
            The title string will be displayed in the plot image
        ``x_label`` String
            Label of histogram x axis.
        ``y_label`` String
            Label of histogram y axis.
        ``bins`` List
            Defines the edges of the bins. Equals the
            number of bins + 1.
            
    *Returns:* String containing full filename of image file, including
    the file extension.
            
    """
    min_bins = 8
    # Clear existing plots from the canvas.
    plt.clf()
    
    # Ensure filename has a ".png" extension
    if not filename.endswith('.png'):
        filename = filename + '.png'
    
    # Convert data to a numpy array
    np_data = np.asanyarray(data, np.int32)

    # Calculate bin sizes if bins are not provided. Ensure bin edges are
    #   integer multiples.
    if bins is None:
        max_value = np.amax(np_data)
        min_value = np.amin(np_data)
        if (max_value - min_value < 10):
            bin_size = 1
        else:
            bin_size = math.ceil((max_value - min_value) / 10)
        bins = []
        bins.append(math.floor(min_value) - bin_size)
        while bins[-1] < max_value:
            bins.append(bins[-1] + bin_size)
        while len(bins) < min_bins:
            bins.append(bins[-1] + bin_size)

    # Create Histogram
    plt.hist(np_data, bins)
    if title is not None:
        plt.title(title)
    if x_label is not None:
        plt.xlabel(x_label)
    if y_label is not None:
        plt.ylabel(y_label)
    
    # Co-locate x-axis ticks with bin boundaries.
    plt.xticks(bins)
        
    # Save Histogram as file
    plt.savefig(folder + '/' + filename)
    
    return filename
    
    
    
        