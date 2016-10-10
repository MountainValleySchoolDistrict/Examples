import matplotlib.pyplot as plt
import numpy as np
import random

if __name__ == '__main__':
    # These values control our test
    num_dice = 10     # The number of dice to roll and sum together
    sides = 20        # How many sides the dice have
    num_tests = 50    # How many rolls we are going to do
    
    # Create an empty list to hold the sums of each roll
    sums = []
    for test in range(num_tests):
        # This line uses a "list comprehension" to simulate a single roll of all the dice
        rolls = [random.randint(1,sides) for _ in range(num_dice)]
        
        # This line adds all the dice values together
        test_sum = sum(rolls)
        
        # This line puts the new sum at the end of our list
        sums.append(test_sum)
    
    # Create a histogram that shows how often each sum appears
    plt.hist(sums, bins=30)