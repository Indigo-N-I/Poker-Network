class Settings():
    ''' class to store settings for poker game'''

    def __init__(self):

        #screen Settings
        self.screen_width = 800
        self.screen_height = 500
        self.bg_color = (200,200,200)

class position():
    ''' position of the cards for game and differetn players'''

    def __init__(self, playerNum, cardNum):
        self.x = 30 + (cardNum-1)*120
        self.y = 40 + (playerNum-1)* 200
        
