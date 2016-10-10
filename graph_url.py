# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 15:31:50 2016

@author: marti
"""
# These lines import the libraries we'll use
import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
import urllib

if __name__ == '__main__':
    # Define a couple of variables: N and url
    N = 10
#    url = 'http://www.google.com'
    url = 'https://www.youtube.com'
    
    # Request the data from the remote website    
    request = urllib.request.urlopen(url)
    
    # Extract the just the html text
    html = request.read()
    
    # Print out the website source code
    print(html)
    
    # Convert the string into an array
    chars = np.fromstring(html,dtype=np.uint8)
    
    # Create a histogram using the data in the array
    plt.hist(chars, bins=N)

#    <a href="........">.....</a>
    #
    # Extra Credit!
    #
    # The next three lines just format the tick marks
    #   on the X-axis.
    #
    #formatter = tick.FuncFormatter(lambda x, i: chr(int(x)))
    #plt.locator_params(axis='x', nbins=N)
    #plt.gca().xaxis.set_major_formatter(formatter)
    
    