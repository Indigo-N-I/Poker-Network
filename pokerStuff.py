import random
import pygame as pg
import os

def cardNum(card):
    return card.getNumber()

def cardNumAce(card):
    return card.getNumber(True)

class Deck():
    #create the deck, unshuffeled
    def __init__(self):
        self._cards = []
        for i in range (1,5):
            for j in range(1,14):
                self._cards.append(Cards(j,i))

    def shuffle(self):
        random.shuffle(self._cards)

    def deal(self):
        self._card = self._cards[0]
        self._cards.remove(self._cards[0])
        return self._card

    def burn(self):
        del self._cards[-1]

    def reset(self):
        self._cards.clear()
        for i in range (1,5):
            for j in range(1,14):
                self._cards.append(Cards(j,i))
        self.shuffle()

    #get size of deck
    def size(self):
        return len(self._cards)

    #get a card
    def getCard(self,number):
        return self._cards[number]

class Cards():
    #create card
    def __init__(self, number, suit):
        self._number = number
        self._suit = suit
        self._png = self.getSpriteName()

    def getNumber(self, maxA = False):
        if maxA and self._number == 1 :
            return 14
        return self._number

    def dealt(self, position):

        self.image = pg.transform.scale(pg.image.load(self._png), (100,145))

        #get card rectangle
        self.rect = self.image.get_rect()

        #position at different positions
        self.rect.centerx = position.x
        self.rect.centery = position.y

    def finishHand(self):
        self.image.fill(transparent)

    '''
    return suit
    1 -> diamond
    2 -> club
    3 -> heart
    4 -> spade
    '''

    def getSpriteName(self):

        current_path = os.path.dirname(__file__)
        resoucePath = os.path.join(current_path, 'PNG-cards-1.3')

        if 1 < self._number < 11:
            name = str(self._number)
        elif self._number == 1:
            name = 'ace'
        elif self._number == 11:
            name = 'jack'
        elif self._number == 12:
            name = 'queen'
        elif self._number == 13:
            name = 'king'

        name += '_of_'

        if self._suit ==1:
            name += 'diamonds'
        elif self._suit == 2:
            name += 'clubs'
        elif self._suit == 3:
            name += 'hearts'
        elif self._suit == 4:
            name += 'spades'

        name +='.png'

        imagePath = os.path.join(resoucePath, name)

        return imagePath

    def getSuit(self):
        return self._suit

    def show(self):
        print(self._number, self._suit)

class Hand():
    #create the cards that you can
    def __init__(self, pocket=[], community=[]):
        self._cards = pocket + community

    def bestHand(self):
        if self._straightFlush():
            return (8, self._highestStraightFlush())
        elif self._fourKind():
            return (7, self._fourKindHand())
        elif self._fullHouse():
            return (6, self._fullHouseHand())
        elif self._flush():
            return (5, self._highestFlush())
        elif self._straight():
            return (4, self._straightHightest())
        elif self._trip():
            return (3, self._tripHand())
        elif self._twoPair():
            return (2, self._pairHand())
        elif self._pair():
            return (1, self._pairHand())
        else:
            self._cards.sort(key = cardNumAce)
            return (0,self._cards[-1].getNumber())
    #determine if you have straight
    def _straight(self):
        self._cards.sort(key = cardNum)
        self._cardNums = [card.getNumber() for card in self._cards]
        if 1 in self._cardNums:
            self._cardNums += [14]
        self._possibleStraight = [self._cardNums[i:i+5] for i in range(len(self._cardNums)) if len(self._cardNums[i:i+5])==5]
        a = []
        for sub in self._possibleStraight:
            a += [list(range(min(sub), max(sub)+1)) == sub]

        return any(a)

    #find highest straight and returns highst number
    def _straightHightest(self):
        self._straights = []
        self._cards.sort(key = cardNum)
        self._cardNums = [card.getNumber() for card in self._cards]
        self._possibleStraight = [self._cardNums[i:i+5] for i in range(len(self._cardNums)) if len(self._cardNums[i:i+5])==5]
        try:
            for sub in self._possibleStraight:
                if set(list(range(min(sub), max(sub)+1))).issubset(set(self._cardNums)):
                    self._straights.append(list(range(min(sub), max(sub)+1)))
            self._straights.sort()
            return self._straights[-1][-1]

        except Exception as e:
            return(14)
    #find if flush
    def _flush(self):
        self._cardSuits = [card.getSuit() for card in self._cards]
        return any([self._cardSuits.count(b) >= 5 for b in self._cardSuits])

    #find highesCard of flush
    def _highestFlush(self):
        self._suitedCards = [card.getNumber(True) for card in self._cards if self._cardSuits.count(card.getSuit()) >=5]
        self._suitedCards.sort()
        self._suitedCards.reverse()
        return self._suitedCards

    #find if straightFlush
    def _straightFlush(self):

        if(self._flush()):
            self._smallHand = Hand([card for card in self._cards if self._cardSuits.count(card.getSuit()) >=5])
            return self._smallHand._straight()

        return False

    #find largest number of straightFlush
    def _highestStraightFlush(self):
        self._cardSuits = [card.getSuit() for card in self._cards]
        self._cardsSuited = []
        for suit in self._cardSuits:
            self._cardsSuited += [[card for card in self._cards if card.getSuit() == suit]]
        self.smallHand = Hand()
        for straightCheck in self._cardsSuited:
            if len(straightCheck) >=5:
                self.smallHand = Hand(straightCheck)

        return self.smallHand._straightHightest()

    #find four of kind
    def _fourKind(self):
        self._cardNums = [card.getNumber() for card in self._cards]
        return any([self._cardNums.count(c) == 4 for c in self._cardNums])

    #find the best five card hand
    def _fourKindHand(self):
        self._cards.sort(key=cardNumAce)
        self._cardsCopy = self._cards.copy()
        self._bestHand = [self._cards[i] for i in range(len(self._cards)) if self._cardNums.count(self._cards[i].getNumber()) == 4]
        for card in self._bestHand:
            self._cardsCopy.remove(card)
        while len(self._bestHand) <5:
            index = len(self._bestHand) - 5
            self._bestHand += [self._cardsCopy[index]]

        return [card.getNumber(True) for card in self._bestHand]

    #see if there is a one pair
    def _pair(self):
        self._cardNums = [card.getNumber() for card in self._cards]
        return any([self._cardNums.count(c) == 2 for c in self._cardNums])

    #get best hand if there is a pair
    def _pairHand(self, handCheck = False):
        index = 0
        self._cards.sort(key=cardNumAce)
        self._cards.reverse()
        self._cardsCopy = self._cards.copy()
        self._bestHand = [self._cards[i] for i in range(-len(self._cards),0) if self._cardNums.count(self._cards[i].getNumber()) == 2]
        self._bestHand.sort(key=cardNumAce)
        for card in self._bestHand:
            self._cardsCopy.remove(card)
        while len(self._bestHand) <5:
            index = len(self._bestHand) - 5
            self._bestHand += [self._cardsCopy[index]]


        if handCheck:
            return self._bestHand

        return [card.getNumber(True) for card in self._bestHand]

    #check for trips
    def _trip(self):
        self._cardNums = [card.getNumber() for card in self._cards]
        return any([self._cardNums.count(c) == 3 for c in self._cardNums])

    #get hand if trips exist
    def _tripHand(self):
        self._cards.sort(key=cardNumAce)
        self._cardsCopy = self._cards.copy()
        self._bestHand = [self._cards[i] for i in range(len(self._cards)) if self._cardNums.count(self._cards[i].getNumber()) == 3]
        for card in self._bestHand:
            self._cardsCopy.remove(card)
        while len(self._bestHand) <5:
            index = len(self._bestHand) - 5
            self._bestHand += [self._cardsCopy[index]]

        return [card.getNumber(True) for card in self._bestHand]

    def _twoPair(self):
        self._smallHand = []
        self._cardNums = []
        if self._pair():
            self._smallHand = self._pairHand(True)

        self._cardNums = [card.getNumber() for card in self._smallHand]
        self._pairsRemoved = [c for c in self._smallHand if not self._cardNums.count(c.getNumber())== 2]
        if len(self._pairsRemoved) ==1:
            return True
        return False

    #find if fullHouse
    def _fullHouse(self):
        if(self._pair() and self._trip()):
            return True
        return False

    #get the full house
    def _fullHouseHand(self):
        self._cards.sort(key=cardNumAce)
        self._bestHand = [self._cards[i] for i in range(len(self._cards)) if self._cardNums.count(self._cards[i].getNumber()) == 3]
        self._bestHand += [self._cards[i] for i in range(len(self._cards)) if self._cardNums.count(self._cards[i].getNumber()) == 2]
        return [card.getNumber(True) for card in self._bestHand]
