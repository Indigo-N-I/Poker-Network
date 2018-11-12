from pokerStuff import Cards

class Player:

    #initate
    def __init__(self, startingMoney, playerPosition):
        self._startingMoney = startingMoney
        self.money = startingMoney
        self._roundBet = 0
        self._position = playerPosition
        self._amountBet = 0
        self._cards = []
        self._folded = 0

    def bet(self, value):
        if value >= self.money:
            self._numberStorage = self.money
            self._amountBet += self.money
            self.money = 0
            self._roundBet += value
            #self.print()
            return self._numberStorage

        else:
            self.money = self.money - value
            self._amountBet += value
            self._roundBet += value
            #self.print()
            return value

    def getMoney(self):
        return self.money

    def allIn(self):
        if self.money == 0:
            return True
        return False

    def addCard(self, card):
        self._cards.append(card)

    #get cards in Hand
    def showCards(self):
        return self._cards

    def winHand(self, pot):
        self.money += pot

    def getPosition(self):
        return self._position

    def fold(self):
        self._cards.clear()
        self._folded +=1

    #returns the cards in Hand
    def getCards(self):
        #print(len(self._cards))
        return[self._cards[0], self._cards[1]]

    def getBet(self):
        return self._roundBet

    def newRound(self):
        self._roundBet=0

    def betInRound(self):
        return self._roundBet

    def print(self):
        print('Player Number:', self._position)
        print('Player Money:', self.money)
        print('Net Change in Money:', self.money - self._startingMoney)

    def getFolds(self):
        return self._folded
