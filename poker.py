from itertools import cycle
import random
from random import randint
import sys

#import pygame
#from pygame.locals import *

import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, LSTM

from pokerStuff import Deck, Cards, Hand
from PokerPlayer import Player

FPS = 60
SCREENHEIGHT = 300.0
SCREENWIDTH = 512.0
STARTINGPOT = 100000
PLAYERS = 6
POT = 0
MINUMUMBET = 1000
BLINDNUMBER = 1

winners = []
numPlayers = 6
currentPoolNum = []
currentPoolSuit = []
currentPoolBetting = []
currentPoolComplete = []
loadSaves = False


def betSame(list):
    return len(set(list))<=1

def savePool():
    for x in range(len(currentPoolNum)):
        currentPoolNum[x].save_weights("SavedModels/models_num" + str(x) + '.keras')
        currentPoolSuit[x].save_weights("SavedModels/models_suit" + str(x) + '.keras')
        currentPoolBetting[x].save_weights("SavedModels/models_bet" + str(x) + '.keras')
        currentPoolComplete[x].save_weights("SavedModels/models_comp" + str(x) + '.keras')
    print("winners saved")

def finishBetting(stillPlaying, bets):
    #print('len(bets) < len(stillPlaying)', len(bets) < len(stillPlaying))

    if len(bets) < len(stillPlaying):
        return False
    elif not betSame([player.betInRound() for player in stillPlaying]):
        maxBet = max([player.betInRound() for player in stillPlaying])
        if any([not player.allIn() for player in stillPlaying if player.getMoney() <= maxBet]):
            return False
        else:
            return True
    else:
        return True

def predictNum(pocket, community, modelNum):
    communityNums = [0 for i in range(min(len(community),5),5)]
    communityNums += [card.getNumber() for card in community]
    neuralInputNums = np.asarray([card.getNumber() for card in pocket.getCards()] + communityNums)
    neuralInputNums = np.atleast_2d(neuralInputNums)
    return currentPoolNum[modelNum].predict(neuralInputNums,1)[0]

def predictSuit(pocket, community, modelNum):
    communitySuit = [0 for i in range(min(len(community),5),5)]
    communitySuit += [card.getSuit() for card in community]
    neuralInputSuit = np.asarray([card.getSuit() for card in pocket.getCards()]+communitySuit)
    neuralInputSuit = np.atleast_2d(neuralInputSuit)
    return currentPoolSuit[modelNum].predict(neuralInputSuit,1)[0]

def predictfromBet(bets,modelNum):
    neuralInputBets = [0 for i in range(min(len(bets),6),6)]
    neuralInputBets += [bets[-i] for i in range(1,7) if i<=len(bets)]
    neuralInputBets = np.asarray(neuralInputBets)
    neuralInputBets = neuralInputBets.reshape((1,6,1))
    return currentPoolBetting[modelNum].predict(neuralInputBets,1)[0]

def predictComplete(money, preNum, preSuit, preBet, maxBet, modelNum):
    inputs = (money, preNum, preSuit, preBet, maxBet)
    inputs = np.asarray(inputs)
    inputs = np.atleast_2d(inputs)
    return currentPoolComplete[modelNum].predict(inputs,1)[0]

def predictAction(pocket, community, bets, modelNum, players, checkallIn = False ):

    preNum = predictNum(pocket, community, modelNum)
    preSuit = predictSuit(pocket, community, modelNum)
    preBet = predictfromBet(bets, modelNum)
    complete = predictComplete(pocket.getMoney(),preNum, preSuit, preBet, max([player.betInRound() for player in players]), modelNum)

    allIn = complete[1]
    if allIn>.85:
        allIn = True
    if checkallIn:
        return allIn

    return complete[0]

def playerOrder(stillPlaying, player):
    afterBlind = stillPlaying[stillPlaying.index(player)+1:]
    wrapAround = stillPlaying[:stillPlaying.index(player)+1]
    return afterBlind + wrapAround

def blinds(stillPlaying):
    global POT
    if BLINDNUMBER>= len(stillPlaying):
        BLINDNUMBER-= len(stillPlaying)
    small = stillPlaying[BLINDNUMBER -1].bet(MINUMUMBET)
    roundBetting.append(small)
    big = stillPlaying[BLINDNUMBER].bet(MINUMUMBET*2)
    roundBetting.append(big)

    POT+= small
    POT+= big

def bet(stillPlaying, blinds = False):
    global POT
    global BLINDNUMBER
    global MINUMUMBET
    toBet = True

    if len(stillPlaying) == 1:
        return stillPlaying

    if blinds:
        blinds(stillPlaying)

    playOrder = playerOrder(stillPlaying, stillPlaying[BLINDNUMBER])
    while not finishBetting(stillPlaying, roundBetting):
        for player in playOrder:
            action = predictAction(player,community,roundBetting,player.getPosition()-1, stillPlaying)
            if round(action/MINUMUMBET)*MINUMUMBET == 0:
                roundBetting.append(0)
                #print(any([not i==0 for i in roundBetting]))
                #print([i for i in roundBetting])
                if( any([not i==0 for i in roundBetting]) and not player.allIn()):
                    player.fold()
                    stillPlaying.remove(player)
                    playOrder.remove(player)
                    #print('no bet', 'removed', player.getPosition())
                #print(len(stillPlaying))
                #print(stillPlaying)
                if len(stillPlaying) ==1:
                    break
            else:
                betAmount = round(action/MINUMUMBET)*MINUMUMBET
                #print('betting', betAmount, 'player', player.getPosition())
                maxBet = max([player.betInRound() for player in stillPlaying])
                if not(predictAction(player,community,roundBetting,player.getPosition()-1, stillPlaying, True)) and (len(roundBetting) > 0 and player.betInRound() < max([others.betInRound() for others in stillPlaying])):
                    player.fold()
                    stillPlaying.remove(player)
                    playOrder.remove(player)

                else:
                    possibleBet = player.bet(betAmount)
                    roundBetting.append(possibleBet)
                    POT+=possibleBet
                    #print('no bet', 'removed', player.getPosition())
                #print(len(stillPlaying)==1)
                #print(stillPlaying)
                if len(stillPlaying) ==1:
                    break
                #print('pot size of', POT)
            #print(betSame([i.getBet() for i in stillPlaying]))
            #print([i.getBet() for i in stillPlaying])
            #print(len(stillPlaying))
        if finishBetting(stillPlaying, roundBetting):
            break
        toBet = False
    for player in players:
        player.newRound()
    roundBetting.clear()

    return stillPlaying

def model_crossover(option = 1):
        # obtain parent weights
    # get random gene
    # swap genes

    global currentPoolNum
    global currentPoolSuit
    global currentPoolBetting
    global currentPoolComplete
    global winners

    weight1 = winners[0][option-1].get_weights()
    weight2 = winners[1][option-1].get_weights()

    new_weights1 = weight1
    new_weights2 = weight2

    gene = int (random.uniform( 0, len (weight1)))

    new_weights1[gene] = weight2[gene]
    new_weights2[gene] = weight1[gene]



    return np.asarray([new_weights1, new_weights2])

def model_mutate(weights, print1 = False):
    # mutate each models weights
    if True:
        for i in range(len(weights)):
            for j in range(len(weights[i])):
                #print(weights[i][j])
                try:
                    for k in range(len(weights[i][j])):
                        if random.uniform(0,1) > .85:
                            change = random.uniform(-0.5,0.5)
                            weights[i][j][k] += change
                except Exception:
                    if random.uniform(0,1) > .85:
                        change = random.uniform(-0.5,0.5)
                        weights[i][j] += change
    return weights

once = False
gen = 1

while True:
    for i in range(numPlayers):

        if len(winners) <2:
            NumModel = Sequential()
            NumModel.add(Dense(4, input_shape=(7,)))
            NumModel.add(Activation('softmax'))
            NumModel.add(Dense(15, input_shape=(3,)))
            NumModel.add(Activation('relu'))
            NumModel.add(Dense(1, input_shape=(15,)))
            NumModel.add(Activation('sigmoid'))

            NumModel.compile(loss = 'mse', optimizer = 'adam', metrics=['accuracy'])
            currentPoolNum.append(NumModel)

            SuitModel = Sequential()
            SuitModel.add(Dense(4, input_shape=(7,)))
            SuitModel.add(Activation('relu'))
            SuitModel.add(Dense(15, input_shape=(4,)))
            SuitModel.add(Activation('relu'))
            SuitModel.add(Dense(1, input_shape=(15,)))
            SuitModel.add(Activation('sigmoid'))
            SuitModel.compile(loss = 'mse', optimizer = 'adam', metrics=['accuracy'])
            currentPoolSuit.append(SuitModel)

            BettingModel = Sequential()

            BettingModel.add(LSTM(15, input_shape=(6,1,)))

            BettingModel.add(Dense(1))
            BettingModel.add(Activation('sigmoid'))

            BettingModel.compile(loss = 'mse', optimizer = 'adam', metrics=['accuracy'])

            '''if not once:
                print('normal weights:', NumModel.get_weights())
                print('lstm weights:', BettingModel.get_weights())
                once = True
'''
            currentPoolBetting.append(BettingModel)

            CompleteModel = Sequential()
            CompleteModel.add(Dense(5, input_shape= (5,)))
            CompleteModel.add(Activation('softplus'))
            CompleteModel.add(Dense(10, input_shape= (5,)))
            CompleteModel.add(Activation('sigmoid'))
            CompleteModel.add(Dense(2, input_shape= (10,)))
            CompleteModel.add(Activation('relu'))

            CompleteModel.compile(loss = 'mse', optimizer = 'adam', metrics=['accuracy'])


            currentPoolComplete.append(CompleteModel)

        if gen>=3:
            for i in range(2):
                currentPoolNum[i].set_weights(winners[i][0].get_weights())
                currentPoolSuit[i].set_weights(winners[i][1].get_weights())
                currentPoolBetting[i].set_weights(winners[i][2].get_weights())
                currentPoolComplete[i].set_weights(winners[i][3].get_weights())

            for i in range(2,3):
                for num in range(1,5):
                    if not num ==3:
                        beforeMutate = model_crossover(num)
                        mutated1 = model_mutate(beforeMutate[0], num ==3)
                        mutated2 = model_mutate(beforeMutate[1], num ==3)
                    else:
                        beforeMutate = model_crossover(num)
                        mutated1 = model_mutate(beforeMutate[0],True)
                        mutated2 = model_mutate(beforeMutate[1], True)
                    if num == 1:
                        currentPoolNum[i].set_weights(mutated1)
                        currentPoolNum[i+2].set_weights(mutated2)
                    elif num ==2:
                        currentPoolSuit[i].set_weights(mutated1)
                        currentPoolSuit[i+2].set_weights(mutated2)
                    elif num ==3:
                        currentPoolBetting[i].set_weights(mutated2)
                        currentPoolBetting[i+2].set_weights(mutated1)
                    elif num == 4:
                        currentPoolComplete[i].set_weights(mutated1)
                        currentPoolComplete[i+2].set_weights(mutated2)

        elif loadSaves:
            for x in range(6):
                currentPoolNum[x].load_weights("SavedModels/models_num" + str(x) + '.keras')
                currentPoolSuit[x].load_weights("SavedModels/models_suit" + str(x) + '.keras')
                currentPoolBetting[x].load_weights("SavedModels/models_bet" + str(x) + '.keras')
                currentPoolComplete[x].load_weights("SavedModels/models_comp" + str(x) + '.keras')

    testDeck = Deck()
    testDeck.shuffle()

    players = []
    stillPlaying = []
    community = []
    roundBetting = []
    gen +=1
    for i in range (PLAYERS):
        newPlayer = Player(STARTINGPOT, i+1)
        players.append(newPlayer)
        #print(players[i].getPosition())

    hands = 0

    while len(players) > 1 and hands <= 100:
        stillPlaying = [player for player in players if player.getMoney() >0]
        #print('numbers of players still playing:', len(stillPlaying))
        for i in range(len(stillPlaying)):
            stillPlaying[i].addCard(testDeck.deal())
            stillPlaying[i].addCard(testDeck.deal())
        # TODO: round of betting

        stillPlaying = bet(stillPlaying,True)
        '''print('after one round betting:')
        for player in stillPlaying:
            print('Player', player.getPosition(), 'has', player.getMoney())
    '''
        print('pot size of', POT)
            #print(didBet)
            #print(roundBetting)

        if len(stillPlaying) > 1:
            testDeck.burn()
            for i in range(3):
                community.append(testDeck.deal())

        # TODO: round of betting
        stillPlaying = bet(stillPlaying)


        if len(stillPlaying) > 1:
            testDeck.burn()
            community.append(testDeck.deal())

        # TODO: round of betting
        stillPlaying = bet(stillPlaying)


        if len(stillPlaying) > 1:
            testDeck.burn()
            community.append(testDeck.deal())

        # TODO: round of betting
        stillPlaying = bet(stillPlaying)

        if len(stillPlaying) > 1:
            playerHands = []
            # TODO: assign winner
            for player in stillPlaying:
                hand = Hand(player.getCards(), community)
                bestHand = hand.bestHand()
                #print(bestHand)
                '''try:
                    #print(playerHands[0])
                except Exception:
                    a = 2'''
                if len(playerHands) ==0:
                        playerHands.append(hand)
                elif hand.bestHand() > playerHands[0].bestHand():
                    playerHands.clear()
                    playerHands.append(hand)

            for player in stillPlaying:
                hand = Hand(player.getCards(), community)
                if not hand.bestHand() == playerHands[0].bestHand():
                    stillPlaying.remove(player)


        #print('pot size of before split', POT)
        POT = POT/len(stillPlaying)
        for player in stillPlaying:
            player.winHand(POT)

        #    print('pot size of after split', POT)


        POT = 0
        #print('pot size of', POT)

        testDeck.reset()
        community.clear()

        #print('after round')

        hands+=1
        for player in players:
            player.newRound()


        if sum([not player.getMoney() ==0 for player in players]) == 1:
            for player in players:
                print('player', player.getPosition(), 'has money', player.getMoney())

            playerNumber = [not player.getMoney() ==0 for player in players].index(1) +1
            break
        if BLINDNUMBER < len(stillPlaying)-1:
            BLINDNUMBER+=1
        else:
            BLINDNUMBER=0


    print('we have a winner')
    print('fold frequency')
    for player in players:
        print('player', player.getPosition(), 'has folded', player.getFolds(), 'out of', hands, 'hands')
    players.clear()

    if len(winners) <2:
        winners.append([currentPoolNum[playerNumber-1], currentPoolSuit[playerNumber-1], currentPoolBetting[playerNumber-1], currentPoolComplete[playerNumber-1]])
    else:
        dedParent = randint(0,1)
        winners[dedParent] = [currentPoolNum[playerNumber-1], currentPoolSuit[playerNumber-1], currentPoolBetting[playerNumber-1], currentPoolComplete[playerNumber-1]]
        savePool()
