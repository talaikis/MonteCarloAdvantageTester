import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as sc
import MySQLdb as mdb
import time

scriptStart = time.time()

#connect to DB
def connect_to_DB():
    
    #Connect to the <a href="http://www.talaikis.com/mysql/">MySQL</a> instance
    db_host = '127.0.0.1'
    db_user = 'root'
    db_pass = '8h^=GP655@740u9'
    db_name = 'lean'

    con = mdb.connect(host = db_host, user = db_user, passwd = db_pass, db = db_name)
    
    return con

#disconnect from databse
def disconnect(con):
    # disconnect from server
    con.close()
    
#get data from <a href="http://www.talaikis.com/mysql/">MySQL</a>
def req_sql(sym, con, period):
    # Select all of the historic close data
    sql = """SELECT DATE_TIME, CLOSE FROM `"""+sym+"""` WHERE DATE_TIME >= (curdate() - interval """+str(period)+""" month) ORDER BY DATE_TIME ASC;"""

     #create a pandas dataframe
    df = pd.read_sql_query(sql, con=con, index_col='DATE_TIME')

    return df

#yeah, simply roll dice
def roll_Returns_dice(params):
    return sc.t.rvs(df=int(params[0]), loc=params[1], scale=params[2], size=100000)

#generate path
def bet_machine(starting_capital, trades, win_rate, id, bankrupt, params, trim):
    
    value = starting_capital
    global bankruptcies
    global bets
    global allReturns
    X = []
    Y = []
    positive_returns = []
    negative_returns = []
    i = 1
    
    #clean values
    returns = roll_Returns_dice(params)
    
    for r in returns:
        if r > 0 and r < trim[1]:
            positive_returns.append(r)
        if r < 0 and r > trim[0]:
            negative_returns.append(r)
    
    lossRate = 100 - win_rate

    #make trading
    while i <= trades:
        #roll the next day
        roll = random.randrange(0, 100)
        if roll > lossRate:
            ret = positive_returns[np.random.randint(low=0, high=len(positive_returns), size=1)]
            value = (1 + ret)*value
            X.append(i)
            Y.append(value)
            allReturns.append(ret)
        else:
            ret = negative_returns[np.random.randint(low=0, high=len(negative_returns), size=1)]
            value = (1 + ret)*value
            X.append(i)
            Y.append(value)
            allReturns.append(ret)
            
            #what if we broke?
            if value <= 0:
                bets.append(i)
                bankruptcies += 1
                if bankrupt:
                    break
            
        i += 1
        
    #default
    if id == 0:
        ax = plt.plot(X, Y)
    if id == 1:
        ax = plt.plot(X, Y, "r")
    if id == 2:
        ax = plt.plot(X, Y, "c")


#script body
if __name__ == "__main__":
    
    #don't touch those
    x = 0
    bets = []
    allReturns = []
    bankruptcies = 0
    con = connect_to_DB()
    
    #inputs
    paths = 100
    periods = 96 #months
    starting_capital = 1000
    
    #get data, fit it, generate a similar sample and see if's similar
    data = req_sql("YAHOO_INDEX_GSPC", con, periods).pct_change().dropna()    
    params = sc.t.fit(data.CLOSE)
    roll = sc.t.rvs(df=params[0], loc=params[1], scale=params[2], size=periods*21)
    
    #make it show something to me
    fig = plt.figure()
    
    ax = fig.add_subplot(2, 2, 1)
    ax = plt.hist(data.CLOSE, bins=300)
    plt.title(s='Empirical distribution')
    
    ax = fig.add_subplot(2, 2, 3)
    ax = plt.hist(roll, bins=300)
    plt.title(s='Simulated distribution')

    ax = fig.add_subplot(2, 2, 2)
    # make patths
    while x < paths:
        bet_machine(starting_capital=starting_capital, trades=100, win_rate=20, id=0, bankrupt=False, params=params, trim=[data.CLOSE.min(), data.CLOSE.max()])
        print "Generated path no. %s" %x
        x += 1
    
    disconnect(con)
    
    #output some simple stats
    if len(bets) == 0:
        bets.append(0)
    data = ((bankruptcies/float(paths))*10.00,
           float(np.mean(bets)),
           float(np.min(bets)),
           float(np.max(bets)))
    print "We got %s percent sold their home broke. \nLosing on average after %s moves. \nUnluckiest member broke after %s bets.\nLuckiest lost everything after %s. " %data
    
    plt.grid(True)
    plt.axhline(0, color = 'r', xmax=5)
    plt.axhline(starting_capital, color = 'g', xmax=5)
    plt.ylabel('Wallet Value')
    plt.xlabel('Trades Count')
    
    ax = fig.add_subplot(2, 2, 4)
    ax = plt.hist(np.sort(allReturns), bins=300)
    plt.title(s='Returns from all paths distribution')
    
    timeused = (time.time()-scriptStart)/60
    print("Done in ",timeused, " minutes")
    
    plt.show()