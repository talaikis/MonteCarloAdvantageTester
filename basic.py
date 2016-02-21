import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

scriptStart = time.time()

#yeah, simply roll dice
def roll_dice(win_rate):
    roll = random.randrange(0, 100)    
    
    wR = 100 - win_rate 
    
    if roll > wR:
        return True
    if roll < wR:
        return False
    
#generate path
def bet_machine(starting_capital, risk_amount, trades, win_rate, id, bankrupt):
    value = starting_capital
    risk = risk_amount

    global bankruptcies
    global bets
    X = []
    Y = []
    i = 1
    
    #make trading
    while i <= trades:
        if roll_dice(win_rate):
            value += risk
            X.append(i)
            Y.append(value)
        else:
            value -= risk
            X.append(i)
            Y.append(value)
            
            #what if we broke?
            if value <= 0:
                bets.append(i)
                bankruptcies += 1
                if bankrupt:
                    break
            
        i += 1
        
    #default
    if id == 0:
        plt.plot(X, Y)
    if id == 1:
        plt.plot(X, Y, "r")
    if id == 2:
        plt.plot(X, Y, "c")

if __name__ == "__main__":
    
    x = 0
    bets = []
    bankruptcies = 0
    
    #you define it
    paths = 100

    # make paths
    while x < paths:
        bet_machine(starting_capital=1000, risk_amount=100, trades=1000, win_rate=54, id=0, bankrupt=False)
        x += 1
    
    data = ((bankruptcies/float(paths))*100.00,
           float(np.mean(bets)),
           float(np.min(bets)),
           float(np.max(bets)))
    print "We got %s percent sold their home broke. \nLosing on average after %s moves. \nUnluckiest member broke after %s bets.\nLuckiest lost everything after %s. " %data
    
    plt.grid(True)
    plt.axhline(0, color = 'r')
    plt.ylabel('Wallet Value')
    plt.xlabel('Trades Count')
    plt.show()
        
    timeused = (time.time()-scriptStart)/60

    print("Done in ",timeused, " minutes")