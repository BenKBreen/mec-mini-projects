







######### ROCK PAPER SCISSORS ########

# Import
import tensorflow as tf
import numpy as np
import math
import random
import re
from collections import Counter
verbose = 0


""" 
### Initialize Game
    M           = Model 
    Pvalue      = integer x in [0..2] where x = 0,1,2 <=>  R,P,S 
    Data        = integer y in [0..9] where y = Pvalue + z where z = 0,1,2 <=>  W,L,T
    P, Q, T     = Wins, losses, ties
    k           = Length of warmup (default = 10)
    m           = Number of Training Epochs (default = 100)
    Warmup      = Flag for warmup
"""

###### Game: Object Type ############
class Game:
    def __init__(self, k = 7, m = 100):
        self.PlayerData = []
        self.OutcomeData = []
        self.W, self.L, self.T = 0, 0, 0 
        self.k = k
        self.m = m
        self.Warmup = True # Warmup Flag

        # Model
        M = tf.keras.Sequential([
            tf.keras.layers.Flatten(input_shape=(k, 6)),
            tf.keras.layers.Dense(6*k, activation='relu'),
            tf.keras.layers.Dense(3)
            ])

        # Compile Model
        M.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])

        self.M = M



# Automatically set up a Game 
G = Game()



########## Model functions ##########

# OneHot 
def OneHot(A):
    A = tf.one_hot(A,6)
    return A


# Train
def Train():
    
    # initialize
    PData = G.PlayerData
    OData = G.OutcomeData
    k = G.k

    n = len(PData) - k
    
    # Training Data + Results 
    TData, TValues = [],[]
    for i in range(n-1):
        Data, Result = OneHot(PData[i:i+k]) + OneHot(OData[i:i+k]), PData[i+k]
        TData.append( Data ) # Players move in games i to i+k-1  
        TValues.append( Result ) # Players move on game i+k

    # append most recent n times 
    for i in range(n):
        Data, Result = OneHot(PData[n-1:n-1+k]) + OneHot(OData[n-1:n-1+k]), PData[n-1+k]
        TData.append( Data ) # Players move in games i to i+k-1  
        TValues.append( Result ) # Players move on game i+k


    # Convert to np arrays
    TData, TValues = np.array(TData), np.array(TValues)

    # Fit 
    G.M.fit( TData, TValues, epochs = G.m, verbose=0 )


########## Predictions ##########

# Prediction (z-score)
def ZscorePredict():
    
    # initialize
    n = len(G.PlayerData) 
    k = min(n,20)

    # data of past games as string 
    Data = ''.join([ str(i) for i in G.PlayerData[::-1] ])
    word = ''

    # ans, max z-score
    ans, z = 0, 0
    for i in range(k):

        # update 
        word += Data[i]
        
        # indices of string - 1 
        ind = [ m.start() - 1 for m in re.finditer(word, Data) if m.start() != 0 ]
        
        if ind: 

            # counts of predictions
            count = Counter( [ Data[i] for i in ind ] )
        
            # prediction
            p = max(count, key=count.get)

            # z-score
            m = len(ind)
            x, mu, sig = count[p], (1/3) * m, (2/9) * math.sqrt(m)
            zs = (x - mu) / sig

            ### Update ###

            # better z-score
            if (z < zs):
                z = zs
                ans = p

    # return 
    return int(ans)



# Prediction (tensor flow)
def Predict():
    
    # initialize
    k = G.k
    n = len(G.PlayerData) 

    # Last k games
    Data = [OneHot( G.PlayerData[n-k:] ) + OneHot( G.OutcomeData[n-k:] )]
    Data = np.array(Data)
    
    # individual prediction
    X = tf.keras.Sequential([ G.M, tf.keras.layers.Softmax()])
    p = X.predict( Data, verbose=0)
    
    # return 
    return np.argmax(p)









########## R/P/S functions ##########

# Initialize 
Converter    = {  "R" : 0,       "r" : 0,        "P" : 1,           "p" : 1,      "S" : 2,      "s" : 2 } # Convert Rock/Paper/Scissors to integer mod 3.
RPSConverter = {    0 : "Rock",    1 : "Paper",    2 : "Scissors" } # integer mod 3 to Rock/Paper/Scissors.
WinConverter = {    3 : "Tie",     4 : "Loss",     5 : "Win" }

# Return winner between x and y 
# The inputs x, y are integers mod 3. We have (x "beats" y)  <=> (x + 1 = y).
def Winner(x,y):
    if x == y: return 3
    elif (x + 1) % 3 == y: return 4
    else: return 5


# Play
def play(p):

    # method = 'tflow'
    method = 'stats'

    # Asserts
    if p not in {0,1,2}:
        if p in "RPSrps": p = Converter[p] # convert R/P/S to integer mod 3
        else: return "You must enter either R / r / 0 = rock, P / p / 1 = Paper, or S / s / 2 = Scissors"

    # AI's move
    if G.Warmup:
        # Random
        q = random.randint(0,2);
    else:
        # Prediction
        q = Predict() if (method == 'tflow') else ZscorePredict() 
        q = (q + 1) % 3 # Counter players move

    # Outcome
    w = Winner(p,q)
    print( "Outcome: {0:10} Player: {1:10} AI: {2}".format( WinConverter[w], RPSConverter[p], RPSConverter[q]) )

    ##### Update #####
    # model
    G.PlayerData += [p] 
    G.OutcomeData += [w]

    # Warmup
    if G.Warmup and G.k == len(G.PlayerData): 
        print( "=" * 50 )
        print("             !! Warmup is over !!         ")
        print("              Let the game begin          ")
        print( "=" * 50 )
        G.Warmup = False
    
    elif not G.Warmup:
        
        # Train
        if (method == 'tflow'): Train()
        
        # Stats
        if w == 5: G.W += 1
        elif w == 4: G.L += 1 
        else: G.T += 1 







########## Stats and Confidence ##########


# Stats 
def Stats():
    print("                           Games", len(G.PlayerData) )
    print( "=" * 60 )
    print("         Wins", G.W, "         Losses", G.L, "         Ties", G.T, "\n") 
    print("Win Percentage", str(round( G.W / (G.W + G.L) * 100, 2)) + "%")


# How Confident is Model
def Confidence():

    # initialize
    Datum = G.Data
    Valum = G.Vals
    k = G.k
    n = len(Datum) - k
    
    # Training Data + Values
    TData, TValues = [],[]
    for i in range(n):
        TData.append( OneHot(Datum[i:i+k]) ) # Players move in games i to i+k-1  
        TValues.append( Valum[i+k] ) # Players move on game i+k

    # Convert to np arrays
    TData, TValues = np.array(TData), np.array(TValues)

    Loss, Acc = G.M.evaluate(TData, TValues, verbose=2)
    print('\nTest accuracy:', Acc)


